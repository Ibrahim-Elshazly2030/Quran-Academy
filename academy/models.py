from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from academy.org_settings import OrganizationSettings  # noqa: F401

class Surah(models.Model):
    """بيانات السور القرآنية لتسهيل التحديد الدقيق للتسميع"""
    number = models.PositiveIntegerField(unique=True, verbose_name=_('رقم السورة'))
    name_arabic = models.CharField(max_length=100, verbose_name=_('اسم السورة'))
    ayah_count = models.PositiveIntegerField(verbose_name=_('عدد الآيات'))
    revelation_place = models.CharField(
        max_length=20,
        choices=[('Meccan', 'مكية'), ('Medinan', 'مدنية')],
        default='Meccan',
        verbose_name=_('مكان النزول')
    )
    start_page = models.PositiveIntegerField(default=1, verbose_name=_('صفحة البداية في المصحف'))
    juz_number = models.PositiveIntegerField(default=1, verbose_name=_('الجزء'))

    class Meta:
        verbose_name = _('سورة قرآنية')
        verbose_name_plural = _('سور القرآن الكريم')
        ordering = ['number']

    def __str__(self):
        return f"{self.number}. سورة {self.name_arabic} ({self.ayah_count} آية)"


class Halaqah(models.Model):
    """المجموعة أو الحلقة القرآنية"""
    class Category(models.TextChoices):
        GENERAL = 'general', _('تحفيظ عام وتأسيس')
        INTENSIVE = 'intensive', _('حفظ مكثف وسريع')
        TAJWEED = 'tajweed', _('إتقان وتجويد وتلاوة')
        KHATMAH = 'khatmah', _('مراجعة وتثبيت للخاتمين')
        IJAZAH = 'ijazah', _('إقراء بالسند والإجازة')
        CHILDREN = 'children', _('براعم وتلقين ناشئة')

    class TimePeriod(models.TextChoices):
        FAJR = 'fajr', _('بعد الفجر')
        MORNING = 'morning', _('الفترة الصباحية')
        ASR = 'asr', _('بعد العصر')
        MAGHRIB = 'maghrib', _('بين المغرب والعشاء')
        ISHA = 'isha', _('بعد العشاء')

    name = models.CharField(max_length=150, verbose_name=_('اسم الحلقة / المجموعة'))
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='taught_halaqat',
        limit_choices_to={'role': 'teacher'},
        verbose_name=_('الشيخ / المعلم المشرف')
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL,
        verbose_name=_('مسار وتصنيف الحلقة')
    )
    days_schedule = models.CharField(
        max_length=150,
        default='السبت، الإثنين، الأربعاء',
        verbose_name=_('أيام الانعقاد')
    )
    time_period = models.CharField(
        max_length=20,
        choices=TimePeriod.choices,
        default=TimePeriod.ASR,
        verbose_name=_('الفترة الزمنية')
    )
    time_detail = models.CharField(
        max_length=100,
        blank=True,
        default='4:30 م - 6:00 م',
        verbose_name=_('التوقيت بالساعات')
    )
    room_location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('المكان / القاعة أو المنصة')
    )
    max_students = models.PositiveIntegerField(
        default=15,
        verbose_name=_('الحد الأقصى للطلاب')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('حالة الحلقة (نشطة)')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('وصف الحلقة وخطة المنهج')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('حلقة قرآنية')
        verbose_name_plural = _('الحلقات القرآنية والمجموعات')
        ordering = ['name']

    def __str__(self):
        teacher_name = self.teacher.get_full_name() or self.teacher.username if self.teacher else 'بدون شيخ'
        return f"{self.name} - (فضيلة الشيخ: {teacher_name})"

    @property
    def current_students_count(self):
        return self.enrollments.filter(status='active').count()

    def get_active_enrollments(self):
        return self.enrollments.filter(status='active').select_related('student')

    def get_active_students(self):
        from accounts.models import User
        active_student_ids = self.enrollments.filter(status='active').values_list('student_id', flat=True)
        return User.objects.filter(id__in=active_student_ids)


class EnrollmentHistory(models.Model):
    """
    سجل التحاق وانتقال الطالب بين المجموعات والشيوخ (يضمن حفظ التاريخ الكامل لكل طالب وشيخ)
    """
    class Status(models.TextChoices):
        ACTIVE = 'active', _('نشط حالياً في الحلقة')
        TRANSFERRED = 'transferred', _('منقول إلى حلقة أخرى')
        GRADUATED = 'graduated', _('أتم المنهج / متخرج')
        PAUSED = 'paused', _('موقوف مؤقتاً')
        WITHDRAWN = 'withdrawn', _('منسحب')

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollment_history',
        limit_choices_to={'role': 'student'},
        verbose_name=_('الطالب')
    )
    halaqah = models.ForeignKey(
        Halaqah,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('الحلقة / المجموعة')
    )
    assigned_sheikh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sheikh_enrollments_supervised',
        limit_choices_to={'role': 'teacher'},
        verbose_name=_('الشيخ المشرف وقت القيد')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_('حالة القيد')
    )
    start_date = models.DateField(
        default=timezone.now,
        verbose_name=_('تاريخ الانضمام للحلقة')
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الانتهاء / النقل')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('ملاحظات النقل أو التقييم الإداري')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_enrollments',
        verbose_name=_('تم الإدراج بواسطة')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ التسجيل'))

    class Meta:
        verbose_name = _('سجل قيد وانتقال')
        verbose_name_plural = _('سجلات قيد وانتقال الطلاب')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.student.display_name} -> {self.halaqah.name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # حفظ الشيخ المشرف تلقائياً وقت تسجيل القيد لضمان التوثيق التاريخي حتى لو تغير شيخ الحلقة مستقبلاً
        if not self.assigned_sheikh and self.halaqah and self.halaqah.teacher:
            self.assigned_sheikh = self.halaqah.teacher
        super().save(*args, **kwargs)
