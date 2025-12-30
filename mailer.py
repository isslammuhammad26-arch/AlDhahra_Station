import smtplib
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def send_daily_report(report_file, chart_file):
    # 1. جلب الإعدادات من قاعدة البيانات
    conn = sqlite3.connect('aldhahra_station.db')
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key='backup_email'")
    target_email = cur.fetchone()[0]
    cur.execute("SELECT value FROM settings WHERE key='cloud_sync'")
    sync_status = cur.fetchone()[0]
    conn.close()

    if target_email == 'not_set' or sync_status == 'off':
        print("ℹ️ المزامنة السحابية معطلة أو الإيميل غير مضبوط.")
        return

    # 2. إعدادات خادم الإرسال (مثال باستخدام Gmail)
    # ملاحظة: يفضل استخدام 'App Password' لضمان الأمان
    sender_email = "yemen.brand.system@gmail.com" 
    sender_password = "your_app_password_here" 

    msg = MIMEMultipart()
    msg['From'] = f"نظام محطة الظهرة <{sender_email}>"
    msg['To'] = target_email
    msg['Subject'] = f"📊 تقرير مبيعات يومي - محطة الظهرة - {os.path.basename(report_file)}"

    body = "أهلاً بك.. مرفق لكم التقرير اليومي المفصل والرسم البياني للأرباح الصافية لمحطة الظهرة.\nصادر عن: وكالة يمن براند للحلول الرقمية."
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 3. إرفاق الملفات (التقرير والصورة)
    for file_path in [report_file, chart_file]:
        if os.path.exists(file_path):
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(file_path)}")
                msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"🚀 تم إرسال التقرير بنجاح إلى: {target_email}")
    except Exception as e:
        print(f"❌ فشل إرسال الإيميل: {e}")

if __name__ == "__main__":
    # تجربة الإرسال (يجب تحديد ملفات موجودة)
    print("جاري فحص المحرك...")
