[app]
title = AlDhahra Station
package.name = aldhahra_erp
package.domain = com.yemenbrand
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

# المتطلبات البرمجية لعام 2025
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,sqlite3

orientation = portrait
fullscreen = 0

# إعدادات الأندرويد المستقرة (حل مشكلة NDK)
android.archs = arm64-v8a
android.accept_sdk_license = True
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_path = 
android.sdk_path = 

# استخدام فرع التطوير لضمان التوافق
p4a.branch = develop

[buildozer]
# تفعيل السجلات التفصيلية لرصد أي توقف
log_level = 2
warn_on_root = 1
