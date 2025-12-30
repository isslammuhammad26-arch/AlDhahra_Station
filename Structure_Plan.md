This system focuses on tracking fuel inventory movement (meter readings) and fundamental financial transactions (sales and expenses) specific to a fuel station operation.

We will provide one integrated Python script (`app.py`) that handles the database initialization, data entry, and calculation logic using SQLite.

---

## 1. Database Schema Design (Internal to `app.py`)

The system will use the following tables:

| Table Name | Purpose | Key Fields |
| :--- | :--- | :--- |
| `Tanks` | Defines physical fuel storage tanks. | `tank_id`, `fuel_type`, `capacity` |
| `Meters` | Defines physical dispensers/nozzles. | `meter_id`, `fuel_type` (e.g., Diesel, Premium 95) |
| `Prices` | Tracks current and historical fuel prices. | `fuel_type`, `unit_price`, `effective_date` |
| `Daily_Readings` | CORE: Stores shift start/end readings and calculated volume. | `reading_id`, `meter_id`, `date`, `shift`, `start_reading`, `end_reading`, `volume_sold` |
| `Sales` | Tracks financial revenue tied to fuel sales. | `sale_id`, `reading_id` (FK), `payment_method` (Cash/Credit), `amount` |
| `Expenses` | Tracks operational costs. | `expense_id`, `date`, `category`, `description`, `amount` |

---

## 2. Python Script (`app.py`)

This script manages the database, initializes settings, and allows for daily meter entry and basic reporting.

```python
# app.py

import sqlite3
from datetime import datetime

DB_NAME = 'aldhahra_station.db'

# --- Database Initialization Functions ---

def initialize_db():
    """Initializes the SQLite database and creates necessary tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Tanks Table (For Inventory Management - Simplified)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tanks (
            tank_id INTEGER PRIMARY KEY,
            fuel_type TEXT NOT NULL UNIQUE,
            capacity REAL NOT NULL
        );
    """)

    # 2. Meters Table (Dispensers/Nozzles)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Meters (
            meter_id INTEGER PRIMARY KEY,
            fuel_type TEXT NOT NULL,
            nozzle_number TEXT UNIQUE
        );
    """)
    
    # 3. Prices Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Prices (
            price_id INTEGER PRIMARY KEY,
            fuel_type TEXT NOT NULL,
            unit_price REAL NOT NULL,
            effective_date DATE NOT NULL
        );
    """)

    # 4. Daily Readings Table (Core Operational Data)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Daily_Readings (
            reading_id INTEGER PRIMARY KEY,
            meter_id INTEGER NOT NULL,
            date DATE NOT NULL,
            shift INTEGER NOT NULL,
            start_reading REAL,
            end_reading REAL,
            volume_sold REAL,
            FOREIGN KEY (meter_id) REFERENCES Meters(meter_id)
        );
    """)

    # 5. Sales Table (Financial Transactions)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Sales (
            sale_id INTEGER PRIMARY KEY,
            reading_id INTEGER,
            date DATE NOT NULL,
            fuel_type TEXT NOT NULL,
            payment_method TEXT NOT NULL, -- 'Cash', 'Credit', 'Fleet'
            amount REAL NOT NULL,
            volume_reported REAL NOT NULL,
            FOREIGN KEY (reading_id) REFERENCES Daily_Readings(reading_id)
        );
    """)

    # 6. Expenses Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Expenses (
            expense_id INTEGER PRIMARY KEY,
            date DATE NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL
        );
    """)

    conn.commit()
    conn.close()

def seed_initial_data():
    """Seeds initial station setup data."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Seed Tanks
    if cursor.execute("SELECT COUNT(*) FROM Tanks").fetchone()[0] == 0:
        cursor.execute("INSERT INTO Tanks (fuel_type, capacity) VALUES ('Premium 95', 30000)")
        cursor.execute("INSERT INTO Tanks (fuel_type, capacity) VALUES ('Diesel', 50000)")
        print("Initialized Tanks.")

    # Seed Meters (Mapping Nozzles to Fuel Types)
    if cursor.execute("SELECT COUNT(*) FROM Meters").fetchone()[0] == 0:
        cursor.execute("INSERT INTO Meters (fuel_type, nozzle_number) VALUES ('Premium 95', 'P1-N1')")
        cursor.execute("INSERT INTO Meters (fuel_type, nozzle_number) VALUES ('Premium 95', 'P1-N2')")
        cursor.execute("INSERT INTO Meters (fuel_type, nozzle_number) VALUES ('Diesel', 'P2-N3')")
        print("Initialized Meters.")
    
    # Seed Prices (Assuming current price)
    if cursor.execute("SELECT COUNT(*) FROM Prices").fetchone()[0] == 0:
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("INSERT INTO Prices (fuel_type, unit_price, effective_date) VALUES (?, ?, ?)", 
                       ('Premium 95', 2.18, today))
        cursor.execute("INSERT INTO Prices (fuel_type, unit_price, effective_date) VALUES (?, ?, ?)", 
                       ('Diesel', 1.55, today))
        print("Initialized Prices.")

    conn.commit()
    conn.close()

# --- Core Logic Functions ---

def get_last_reading(meter_id):
    """Retrieves the last recorded end reading for a specific meter."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Get the latest reading recorded for this meter
    cursor.execute("""
        SELECT end_reading 
        FROM Daily_Readings 
        WHERE meter_id = ? 
        ORDER BY reading_id DESC 
        LIMIT 1
    """, (meter_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    # If no previous reading exists, start from 0
    return result[0] if result else 0.0

def enter_meter_readings():
    """CLI for entering meter readings for a new shift."""
    
    print("\n--- ENTER DAILY/SHIFT READINGS ---")
    
    try:
        date_str = input("Enter Date (YYYY-MM-DD, default today): ") or datetime.now().strftime('%Y-%m-%d')
        shift = int(input("Enter Shift Number (e.g., 1 or 2): "))
    except ValueError:
        print("Invalid input for shift number.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Fetch all meters
    meters = cursor.execute("SELECT meter_id, fuel_type, nozzle_number FROM Meters ORDER BY meter_id").fetchall()
    
    if not meters:
        print("Error: No meters defined in the system.")
        conn.close()
        return

    current_sales_data = []

    for meter_id, fuel_type, nozzle in meters:
        start_reading = get_last_reading(meter_id)
        
        # Check if reading has already been entered for this shift/date
        check = cursor.execute("SELECT reading_id FROM Daily_Readings WHERE date=? AND shift=? AND meter_id=?", 
                               (date_str, shift, meter_id)).fetchone()
        if check:
            print(f"Skipping {nozzle}: Reading already entered for this shift.")
            continue
            
        print(f"\n--- Meter: {nozzle} ({fuel_type}) ---")
        print(f"  Starting Reading: {start_reading:.3f}")
        
        while True:
            try:
                end_reading = float(input("  Enter Current End Reading: "))
                if end_reading < start_reading:
                    print("Error: End reading cannot be less than the start reading.")
                    continue
                break
            except ValueError:
                print("Invalid numerical input.")
                
        volume_sold = end_reading - start_reading
        
        # 1. Insert into Daily_Readings
        cursor.execute("""
            INSERT INTO Daily_Readings (meter_id, date, shift, start_reading, end_reading, volume_sold)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (meter_id, date_str, shift, start_reading, end_reading, volume_sold))
        
        new_reading_id = cursor.lastrowid
        print(f"  => Calculated Volume Sold: {volume_sold:.2f} L")

        # 2. Collect Financial Data (Simplified for CLI)
        current_price = cursor.execute("SELECT unit_price FROM Prices WHERE fuel_type=? ORDER BY effective_date DESC LIMIT 1", (fuel_type,)).fetchone()
        price = current_price[0] if current_price else 0.0
        
        print(f"  (Price: {price:.2f} SAR/L)")
        
        # Ask for financial breakdown
        while True:
            try:
                cash_amount = float(input(f"  Enter Cash Revenue collected for {volume_sold:.2f}L: "))
                credit_amount = float(input("  Enter Credit/Invoice Revenue: "))
                
                total_reported_revenue = cash_amount + credit_amount
                calculated_revenue = volume_sold * price
                
                print(f"  Calculated Revenue: {calculated_revenue:.2f} | Reported: {total_reported_revenue:.2f}")
                
                # Basic variance check
                if abs(total_reported_revenue - calculated_revenue) > 5.0: # 5 SAR tolerance
                    print("WARNING: Significant variance between calculated and reported revenue.")
                
                # Insert Cash Sale
                cursor.execute("""
                    INSERT INTO Sales (reading_id, date, fuel_type, payment_method, amount, volume_reported)
                    VALUES (?, ?, ?, 'Cash', ?, ?)
                """, (new_reading_id, date_str, fuel_type, cash_amount, volume_sold))
                
                # Insert Credit Sale (Only if positive)
                if credit_amount > 0:
                    cursor.execute("""
                        INSERT INTO Sales (reading_id, date, fuel_type, payment_method, amount, volume_reported)
                        VALUES (?, ?, ?, 'Credit', ?, 0.0)
                    """, (new_reading_id, date_str, fuel_type, credit_amount))
                
                break
            except ValueError:
                print("Invalid input for revenue amount.")
                
    conn.commit()
    conn.close()
    print("\nSuccessfully recorded all shift readings and sales.")


def enter_expense():
    """Allows entry of operational expenses."""
    print("\n--- ENTER EXPENSE ---")
    try:
        date_str = input("Enter Date (YYYY-MM-DD, default today): ") or datetime.now().strftime('%Y-%m-%d')
        category = input("Enter Category (e.g., Salary, Utilities, Maintenance): ")
        description = input("Enter Description: ")
        amount = float(input("Enter Amount (SAR): "))
    except ValueError:
        print("Invalid amount entered.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Expenses (date, category, description, amount)
        VALUES (?, ?, ?, ?)
    """, (date_str, category, description, amount))
    conn.commit()
    conn.close()
    print(f"Expense of {amount:.2f} SAR recorded.")

# --- Reporting Functions ---

def daily_shift_summary():
    """Generates a summary of sales and volume for a specific date/shift."""
    print("\n--- DAILY SHIFT SUMMARY REPORT ---")
    
    date_str = input("Enter Date for report (YYYY-MM-DD): ")
    shift_str = input("Enter Shift Number (Optional, leave blank for all shifts): ")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Base query for volume and sales
    query = """
    SELECT 
        M.fuel_type, 
        SUM(D.volume_sold), 
        SUM(CASE WHEN S.payment_method = 'Cash' THEN S.amount ELSE 0 END),
        SUM(CASE WHEN S.payment_method = 'Credit' THEN S.amount ELSE 0 END)
    FROM Daily_Readings D
    JOIN Meters M ON D.meter_id = M.meter_id
    LEFT JOIN Sales S ON D.reading_id = S.reading_id
    WHERE D.date = ?
    """
    params = [date_str]
    
    if shift_str:
        try:
            shift = int(shift_str)
            query += " AND D.shift = ?"
            params.append(shift)
        except ValueError:
            print("Invalid shift number.")
            conn.close()
            return
            
    query += " GROUP BY M.fuel_type;"

    results = cursor.execute(query, params).fetchall()
    
    if not results:
        print(f"No data found for {date_str} (Shift {shift_str if shift_str else 'All'}).")
        conn.close()
        return

    print(f"\n--- Report for {date_str} (Shift {shift_str if shift_str else 'All'}) ---")
    print(f"{'Fuel Type':<15}{'Volume (L)':>15}{'Cash Sales (SAR)':>20}{'Credit Sales (SAR)':>20}")
    print("-" * 70)
    
    total_volume = 0
    total_cash = 0
    total_credit = 0

    for fuel, volume, cash, credit in results:
        print(f"{fuel:<15}{volume:>15.2f}{cash:>20.2f}{credit:>20.2f}")
        total_volume += volume
        total_cash += cash
        total_credit += credit
        
    print("-" * 70)
    print(f"{'TOTALS':<15}{total_volume:>15.2f}{total_cash:>20.2f}{total_credit:>20.2f}")

    # Report Expenses
    expenses = cursor.execute("SELECT SUM(amount) FROM Expenses WHERE date = ?", (date_str,)).fetchone()[0] or 0.0
    print(f"\nTotal Operational Expenses reported for {date_str}: {expenses:.2f} SAR")

    conn.close()


# --- Main Application Loop ---

def main():
    initialize_db()
    seed_initial_data()
    
    while True:
        print("\n=== Al-Dhahra Station Accounting System ===")
        print("1. Enter Shift Meter Readings & Sales")
        print("2. Record Operational Expense")
        print("3. View Daily Shift Summary Report")
        print("4. Exit")
        
        choice = input("Enter choice: ")
        
        if choice == '1':
            enter_meter_readings()
        elif choice == '2':
            enter_expense()
        elif choice == '3':
            daily_shift_summary()
        elif choice == '4':
            print("Exiting system. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
```

### Instructions to Run:

1.  **Save:** Save the code above as `app.py`.
2.  **Run:** Execute the script from your terminal:
    ```bash
    python app.py
    ```
3.  **Usage:**
    *   The first run will create the `aldhahra_station.db` file and initialize the tanks and meters.
    *   Use option `1` to enter readings. The system will automatically retrieve the previous shift's `end_reading` to use as the current shift's `start_reading`, ensuring accurate calculation of `volume_sold`.
    *   Use option `3` to generate reports.