from django.db import models
from django.utils.translation import gettext_lazy as _


class OrganizationSettings(models.Model):
    """
    إعدادات المنشأة / الأكاديمية القرآنية
    نموذج Singleton: سجل واحد فقط يمثل هوية المنشأة
    يظهر اسمها وشعارها وبياناتها في كافة الصفحات والتقارير الرسمية
    """
    name = models.CharField(
        max_length=200,
        default='منظومة صرح القرآن الكريم',
        verbose_name=_('اسم المنشأة / الأكاديمية')
    )
    name_en = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name=_('اسم المنشأة بالإنجليزية (اختياري)')
    )
    slogan = models.CharField(
        max_length=300,
        blank=True,
        default='المنظومة التعليمية لإدارة الحلقات والمدارس القرآنية',
        verbose_name=_('الشعار / العبارة التعريفية')
    )
    logo = models.ImageField(
        upload_to='org/',
        null=True,
        blank=True,
        verbose_name=_('شعار المنشأة (Logo)')
    )
    logo_icon_letter = models.CharField(
        max_length=5,
        default='ق',
        verbose_name=_('الحرف الاختصاري للشعار (يظهر عند عدم رفع صورة)')
    )

    # --- بيانات التواصل ---
    phone_primary = models.CharField(
        max_length=30, blank=True,
        verbose_name=_('رقم الهاتف الرئيسي')
    )
    phone_secondary = models.CharField(
        max_length=30, blank=True,
        verbose_name=_('رقم هاتف إضافي')
    )
    email = models.EmailField(
        blank=True,
        verbose_name=_('البريد الإلكتروني الرسمي')
    )
    website = models.URLField(
        blank=True,
        verbose_name=_('الموقع الإلكتروني')
    )
    address = models.TextField(
        blank=True,
        verbose_name=_('العنوان الكامل للمقر الرئيسي')
    )
    city = models.CharField(
        max_length=100, blank=True,
        verbose_name=_('المدينة')
    )
    country = models.CharField(
        max_length=100, blank=True,
        default='المملكة العربية السعودية',
        verbose_name=_('الدولة')
    )

    # --- البيانات الرسمية ---
    license_number = models.CharField(
        max_length=100, blank=True,
        verbose_name=_('رقم الترخيص / السجل الرسمي')
    )
    founding_year = models.CharField(
        max_length=10, blank=True,
        verbose_name=_('سنة التأسيس')
    )
    supervisor_name = models.CharField(
        max_length=150, blank=True,
        verbose_name=_('اسم المشرف العام / المدير التنفيذي')
    )
    supervisor_title = models.CharField(
        max_length=100, blank=True,
        default='مدير عام المنظومة القرآنية',
        verbose_name=_('لقب / مسمى المشرف العام')
    )
    scientific_director = models.CharField(
        max_length=150, blank=True,
        verbose_name=_('مدير الشؤون التعليمية والقرآنية')
    )

    # --- رسالة التذييل في التقارير ---
    report_footer_quote = models.CharField(
        max_length=300, blank=True,
        default='خَيْرُكُمْ مَنْ تَعَلَّمَ الْقُرْآنَ وَعَلَّمَهُ',
        verbose_name=_('الآية / الحديث في تذييل التقارير')
    )
    report_footer_note = models.TextField(
        blank=True,
        verbose_name=_('ملاحظة ختامية في التقارير (اختياري)')
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('إعدادات المنشأة')
        verbose_name_plural = _('إعدادات المنشأة')

    def __str__(self):
        return self.name

    @classmethod
    def get_settings(cls):
        """الحصول على إعدادات المنشأة (يُنشئها تلقائياً إذا لم تكن موجودة)"""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def logo_display(self):
        """يعيد URL الشعار أو None إذا لم يكن موجوداً"""
        if self.logo:
            return self.logo.url
        return None
