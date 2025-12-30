import sqlite3

def init_db():
    conn = sqlite3.connect('aldhahra_station.db')
    cursor = conn.cursor()
    
    # 1. جدول المستخدمين المطور (تعدد المحاسبين)
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       username TEXT UNIQUE, 
                       password TEXT, 
                       role TEXT)''') # Role: 'admin' or 'accountant'
    
    # إضافة المدير الافتراضي (إذا لم يكن موجوداً)
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', '123', 'admin')")
    
    # 2. تحديث جدول الورديات لإضافة حقل "اسم المحاسب"
    cursor.execute('''CREATE TABLE IF NOT EXISTS shifts 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       date TEXT, product TEXT, liters_sold REAL, 
                       net_required REAL, shortage REAL, surplus REAL,
                       recorded_by TEXT)''')

    # الجداول الأخرى تبقى لضمان التكامل
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("INSERT OR IGNORE INTO settings VALUES ('station_name', 'محطة الظهرة')")

    conn.commit()
    conn.close()
    print("✅ تم تفعيل نظام تعدد المستخدمين والرقابة الرقمية!")

if __name__ == "__main__":
    init_db()
