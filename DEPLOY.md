# دليل النشر الحقيقي لمشروع Furqan Quran Academy

## 1) متطلبات النشر

- Python 3.10+
- PostgreSQL (موصى به للإنتاج)
- Nginx أو خادم Reverse Proxy
- Gunicorn
- SSL/TLS (اختياري لكنه موصى به)
- Domain أو IP ثابت

## 2) إعداد البيئة

أنشئ ملف `.env` بناءً على `.env.example` وقم بتحديث القيم التالية:

```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your_long_secure_secret_key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
USE_POSTGRESQL=True
DB_NAME=quran_academy_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=5432
LANGUAGE_CODE=ar
TIME_ZONE=Asia/Riyadh
```

## 3) تثبيت التبعيات

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4) إنشاء قاعدة البيانات

```bash
python manage.py migrate
python manage.py createsuperuser
```

## 5) تجميع الملفات الثابتة

```bash
python manage.py collectstatic --noinput
```

## 6) بدء التشغيل في بيئة الإنتاج

في بيئة Linux أو خادم حقيقي، يمكن استخدام Gunicorn كما يلي:

```bash
gunicorn config.wsgi:application -c gunicorn.conf.py
```

أما على نظام Windows المحلي للتجربة، يفضل تشغيل المشروع عبر:

```bash
start_production_server.bat
```

> ملاحظة: Gunicorn يعتمد على مكتبات Unix مثل `fcntl`، لذلك قد يحدث خطأ عند التشغيل مباشرة على Windows. لهذا السبب تم تهيئة ملف التشغيل المحلي لاستخدام `manage.py runserver` على المنفذ 8005 كنسخة إنتاجية محاكاة.

## 7) مثال تكوين Nginx

أنشئ ملفًا باسم `nginx.conf.example` أو أضف هذا الكود داخل إعدادات الموقع:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /path/to/project/staticfiles/;
    }

    location /media/ {
        alias /path/to/project/media/;
    }

    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:8005;
    }
}
```

## 8) قائمة فحص النشر

- [ ] تم ضبط `DEBUG=False`
- [ ] تم ضبط `ALLOWED_HOSTS` بدقة
- [ ] تم إعداد `SECRET_KEY` بشكل آمن
- [ ] تم ضبط `USE_POSTGRESQL=True` في الإنتاج
- [ ] تم إنشاء قاعدة البيانات بنجاح
- [ ] تم تنفيذ `migrate`
- [ ] تم إنشاء مستخدم إداري
- [ ] تم تنفيذ `collectstatic`
- [ ] تم تشغيل Gunicorn بنجاح
- [ ] تم توجيه الطلبات من Nginx إلى التطبيق
- [ ] تم اختبار الموقع عبر HTTPS

## 9) الملاحظات النهائية

هذه الخطوات جاهزة للاستخدام كقاعدة للإطلاق الحقيقي للمشروع، مع إمكانية لاحقًا إضافة:
- النسخ الاحتياطي التلقائي للبيانات
- مراقبة الأخطاء عبر Sentry
- النسخ الاحتياطي اليومي للـ DB
- نظام CI/CD
