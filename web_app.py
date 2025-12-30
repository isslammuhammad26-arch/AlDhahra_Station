from flask import Flask, render_template_string
import sqlite3
import os

app = Flask(__name__)

# المسار الصحيح لقاعدة البيانات في Termux
DB_PATH = os.path.join(os.getcwd(), 'aldhahra_station.db')

@app.route('/')
def home():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users") # فحص وجود المستخدمين
        data = cur.fetchall()
        conn.close()
        return f"<h1>محطة الظهرة - يمن براند</h1><p>عدد المستخدمين المسجلين: {len(data)}</p>"
    except Exception as e:
        return f"خطأ في قاعدة البيانات: {e}"

if __name__ == '__main__':
    # التشغيل على لوكالهوست (Localhost)
    app.run(host='0.0.0.0', port=5000, debug=True)
