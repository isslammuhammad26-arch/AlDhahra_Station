import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

def generate_visual_report():
    conn = sqlite3.connect('aldhahra_station.db')
    cursor = conn.cursor()
    
    # 1. جلب بيانات الأرباح الصافية حسب التاريخ
    cursor.execute("""
        SELECT date, SUM((selling_price - 950) * liters_sold - expenses) 
        FROM shifts 
        GROUP BY date 
        ORDER BY date ASC
    """)
    data = cursor.fetchall()
    
    if not data:
        print("⚠️ لا توجد بيانات كافية لتوليد الرسم البياني.")
        return

    dates = [row[0] for row in data]
    profits = [row[1] for row in data]

    # 2. تصميم الرسم البياني بشكل جذاب (يمن براند ستايل)
    plt.figure(figsize=(10, 6))
    plt.plot(dates, profits, marker='o', linestyle='-', color='#1a73e8', linewidth=2, label='صافي الربح اليومي')
    plt.fill_between(dates, profits, color='#1a73e8', alpha=0.1)
    
    plt.title('📈 تحليل نمو الأرباح الصافية - محطة الظهرة', fontsize=16, pad=20)
    plt.xlabel('التاريخ', fontsize=12)
    plt.ylabel('الربح الصافي (ريال)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    # 3. حفظ الرسم البياني كصورة احترافية
    report_name = f"Profit_Chart_{datetime.now().strftime('%Y%m%d')}.png"
    plt.savefig(report_name)
    plt.close()
    
    print(f"✅ تم توليد الرسم البياني بنجاح: {report_name}")
    print("💡 يمكنك الآن فتح هذه الصورة وإرسالها لصاحب المحطة كتقرير احترافي.")

if __name__ == "__main__":
    generate_visual_report()
