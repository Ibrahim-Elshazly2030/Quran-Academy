# منصة Furqan Quran Academy

منصة عربية متكاملة لإدارة أكاديمية تحفيظ القرآن الكريم، وتغطي كل مراحل تنظيم الحلقات القرآنية، إدارة الطلاب، متابعة الحضور، التقييمات، والتقارير الإدارية.

## نظرة عامة

يهدف المشروع إلى دعم إدارة المعهد أو الأكاديمية القرآنية من خلال:

- إدارة المستخدمين حسب الدور: مدير، شيخ، طالب
- إدارة الحلقات والمجموعات القرآنية
- تسجيل الطلاب في الحلقات وانتقالهم بين الحلقات
- متابعة الحضور والغياب
- تقييم الأداء القرآني والمهارات التلاوة
- إعداد تقارير إدارية ولوحيات متابعة
- دعم قاعدة بيانات SQLite افتراضيًا مع إمكانية استخدام PostgreSQL

## المميزات الرئيسية

- واجهة إدارة مركزية للأكاديمية
- إدارة شيوخ الحلقات والمعلمين
- إدارة الطلاب وملفاتهم الشخصية
- هيكلة حلقات حسب المسار: تحفيظ عام، intensive، تجويد، مراجعة، إجازة
- إدارة الجداول الزمنية وأيام الحلقات
- تتبع السجل التاريخي للانضمام والنقل والتخرج
- تقارير لكل من الإدارة والشيخ والطّالب
- دعم التعدد اللغوي (العربية) مع إعدادات المنطقة الزمنية

## التقنية المستخدمة

- Python 3.10+
- Django
- SQLite (الافتراضي)
- PostgreSQL (اختياري)
- Bootstrap / Templates Django
- dotenv لإدارة متغيرات البيئة

## هيكل المشروع

```text
quran_academy/
├── academy/                  # إدارة الحلقات والطلاب والتسجيلات
├── accounts/                 # المستخدمون والأدوار والصلاحيات
├── attendance/               # حضور الطلاب وتقارير الحضور
├── evaluations/              # معايير التقييم وجلسات الاختبار
├── reports/                  # التقارير والتحليلات
├── templates/                 # ملفات HTML للقوالب
├── static/                   # ملفات CSS, JS, الصور
├── media/                    # ملفات الوسائط
├── config/                   # إعدادات Django ومشروع التطبيق
├── manage.py                 # نقطة تشغيل المشروع
├── .env.example              # مثال لقيم البيئة
├── db.sqlite3                # قاعدة بيانات SQLite محلية
├── setup_postgres.py          # إعداد PostgreSQL
├── README.md                 # ملف التوثيق
└── venv/                     # بيئة افتراضية محلية
```

## متطلبات التشغيل

تأكد من توفر التالي على جهازك:

- Python 3.10 أو أحدث
- pip
- Git
- (اختياري) PostgreSQL إذا كنت تريد استخدام قاعدة بيانات خارجية

## خطوات التثبيت

### 1) استنساخ المشروع

```bash
git clone <رابط_المشروع>
cd quran_academy
```

### 2) إنشاء بيئة افتراضية

#### على Windows

```powershell
python -m venv venv
.\venv\Scripts\activate
```

#### على Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3) تثبيت المكتبات المطلوبة

```bash
pip install django python-dotenv pillow psycopg2-binary
```

> إذا كنت ستستخدم SQLite فقط، فحزمة `psycopg2-binary` ليست ضرورية، لكن تثبيتها لا يضر.

### 4) إعداد متغيرات البيئة

انسخ ملف المثال إلى ملف `.env`:

```bash
copy .env.example .env
```

ثم عدّل قيم الملف حسب البيئة لديك، مثال:

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
USE_POSTGRESQL=False
DB_NAME=quran_academy_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=5432
```

> ملاحظة: الافتراضي في المشروع هو SQLite. إذا تركت `USE_POSTGRESQL=False` فسيعمل المشروع على `db.sqlite3` بدون إعدادات إضافية.

### 5) تشغيل الهجرات

```bash
python manage.py migrate
```

### 6) إنشاء مستخدم إداري

```bash
python manage.py createsuperuser
```

### 7) تشغيل المشروع

لأن هناك مشاريع أخرى قيد التشغيل، تم تحديد المنفذ 8005 لهذا المشروع:

```bash
python manage.py runserver 0.0.0.0:8005
```

أو عبر البيئة الافتراضية:

```bash
.\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8005
```

ثم افتح المتصفح في:

- http://127.0.0.1:8005/
- http://127.0.0.1:8005/accounts/login/
- http://127.0.0.1:8005/django-admin/

## بيانات تجريبية (اختياري)

يوجد أمر جاهز لملء قاعدة البيانات ببيانات تمثيلية، بما في ذلك:

- السور القرآنية
- المستخدمين التجريبيين
- الشيوخ
- الطلاب
- الحلقات
- بعض بيانات التقييم والحضور

لتنفيذها:

```bash
python manage.py seed_data
```

## حسابات تجريبية

إذا تم تشغيل الأمر `seed_data` فغالبًا ستتوفر حسابات مثل:

- المدير: `admin` / كلمة المرور: `admin123`
- الشيخ: `sheikh_ahmed` / كلمة المرور: `sheikh123`
- الطالب: `student_omar` / كلمة المرور: `student123`

## الوصول إلى الواجهات

- لوحة الإدارة: `/admin-panel/`
- لوحة الشيخ: `/sheikh/`
- صفحة تسجيل الدخول: `/accounts/login/`
- لوحة إدارة Django: `/django-admin/`

## استخدام PostgreSQL

إذا رغبت في توصيل المشروع بـ PostgreSQL، فقم بما يلي:

1. ضبط `USE_POSTGRESQL=True`
2. إضافة بيانات الاتصال في ملف `.env`
3. إنشاء قاعدة البيانات في PostgreSQL
4. تشغيل:

```bash
python manage.py migrate
```

هناك أيضًا ملف إعدادات جاهز في `setup_postgres.py`، ويمكن استخدامه كمرجع لتجهيز قاعدة البيانات.

## ملاحظات مهمة

- الملف الرئيسي للإعدادات موجود في `config/settings.py`
- ملف توجيه المسارات الرئيسي هو `config/urls.py`
- القوالب موجودة داخل مجلد `templates/`
- يتم التعامل مع الصور الشخصية والملفات الوسائط عبر `MEDIA_ROOT`

## المساهمة

إذا أردت المشاركة في تطوير المشروع:

1. افتح فرعًا جديدًا
2. اجعل التعديلات واضحة ومقسمة
3. أضف اختبارات مناسبة عند الضرورة
4. أرسل طلب دمج (Pull Request)

## الترخيص

هذا المشروع مخصص للاستخدام الداخلي للمؤسسة أو الأكاديمية، ويعتمد على سياسة الترخيص الخاصة بالمطور أو المؤسسة المالكة.

## التشغيل النهائي للإنتاج

### 1) إعداد البيئة الإنتاجية

أنشئ ملف `.env` يحتوي على القيم الحقيقية للإنتاج، مع مراعاة ما يلي:

```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your_very_secure_secret_key_here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
USE_POSTGRESQL=True
DB_NAME=quran_academy_db
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=5432
LANGUAGE_CODE=ar
TIME_ZONE=Asia/Riyadh
```

### 2) إنشاء قاعدة البيانات

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 3) تجميع الملفات الثابتة

```bash
python manage.py collectstatic
```

### 4) تشغيل التطبيق بطريقة إنتاجية

```bash
gunicorn config.wsgi:application -c gunicorn.conf.py
```

أو عبر ملف التشغيل المجهز:

```bash
start_production_server.bat
```

### 5) النشر عبر خادم HTTP

يوصى باستخدام:
- Nginx كخادم أمامي
- Gunicorn كخادم تطبيق
- SSL/HTTPS
- PostgreSQL كقاعدة بيانات الإنتاج

## قائمة الفحص النهائية قبل الإطلاق

- [ ] تم ضبط `DEBUG=False`
- [ ] تم تعيين `SECRET_KEY` حقيقي ومميز
- [ ] تم ضبط `ALLOWED_HOSTS` بدقة
- [ ] تم تثبيت جميع المكتبات من `requirements.txt`
- [ ] تم تشغيل `migrate` بنجاح
- [ ] تم إنشاء حساب مدير أولي
- [ ] تم التحقق من صلاحيات المشرف/الشيخ/الطالب
- [ ] تم اختبار عرض التقارير وحظور الطلاب
- [ ] تم جمع الملفات الثابتة `collectstatic`
- [ ] تم ضبط اتصال PostgreSQL أو SQLite حسب الوضع
- [ ] تم اختبار رابط الموقع في المتصفح
- [ ] تم التأكد من وجود نسخة احتياطية للبيانات

## التواصل

إذا كنت بحاجة إلى دعم إضافي أو تريد تخصيص المشروع لاحتياجات أكاديمية معينة، يمكنك تعديل القوالب والنماذج والربط حسب المتطلبات المحلية.
