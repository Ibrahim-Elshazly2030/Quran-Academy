"""
سكربت تهيئة قاعدة بيانات PostgreSQL للأكاديمية القرآنية
يقوم بالاتصال بخادم PostgreSQL وإنشاء قاعدة البيانات quran_academy_db إذا لم تكن موجودة.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# تحميل المتغيرات من .env
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

db_name = os.getenv('DB_NAME', 'quran_academy_db')
db_user = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD', '')
db_host = os.getenv('DB_HOST', '127.0.0.1')
db_port = os.getenv('DB_PORT', '5432')

print("=" * 60)
print(" تهيئة قاعدة بيانات PostgreSQL لمنظومة الحلقات القرآنية")
print("=" * 60)
print(f"المخدم: {db_host}:{db_port}")
print(f"المستخدم: {db_user}")
print(f"اسم قاعدة البيانات المستهدفة: {db_name}")
print("-" * 60)

try:
    import psycopg
    from psycopg import sql
except ImportError:
    try:
        import psycopg2 as psycopg
        from psycopg2 import sql
    except ImportError:
        print("[!] خطأ: حزمة psycopg غير مثبتة. يرجى تشغيل: pip install 'psycopg[binary]'")
        sys.exit(1)

try:
    # الاتصال بقاعدة البيانات الافتراضية postgres لإنشاء قاعدة بيانات المشروع
    conn = psycopg.connect(
        dbname="postgres",
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        autocommit=True
    )
    cursor = conn.cursor()
    
    # التحقق من وجود قاعدة البيانات
    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
    exists = cursor.fetchone()
    
    if not exists:
        print(f"[+] جاري إنشاء قاعدة البيانات '{db_name}'...")
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        print(f"[OK] Database '{db_name}' created successfully in PostgreSQL!")
    else:
        print(f"[i] Database '{db_name}' already exists.")
        
    cursor.close()
    conn.close()
    print("[OK] Connection and setup completed successfully! You can run manage.py migrate")
except Exception as e:
    print(f"[X] تعذر الاتصال بـ PostgreSQL: {e}")
    print("يرجى التأكد من صحة كلمة المرور واسم المستخدم في ملف .env")
