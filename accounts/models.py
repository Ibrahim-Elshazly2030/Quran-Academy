from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', _('مدير / مشرف إداري')
        TEACHER = 'teacher', _('شيخ / معلم محفظ')
        STUDENT = 'student', _('طالب')

    class Gender(models.TextChoices):
        MALE = 'male', _('ذكر')
        FEMALE = 'female', _('أنثى')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name=_('نوع الحساب / الدور')
    )
    national_id = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_('رقم الهوية / الإقامة')
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('رقم الهاتف')
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الميلاد')
    )
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        default=Gender.MALE,
        verbose_name=_('الجنس')
    )
    address = models.TextField(
        blank=True,
        verbose_name=_('العنوان السكني')
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name=_('الصورة الشخصية')
    )

    # --- بيانات خاصة بالشيخ / المعلم ---
    ijazah_details = models.TextField(
        blank=True,
        verbose_name=_('الإجازات القرآنية والروايات والسند'),
        help_text=_('مثل: إجازة برواية حفص عن عاصم، قراءة ابن كثير...')
    )
    qualification = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('المؤهل العلمي / الشرعي')
    )
    years_of_experience = models.PositiveIntegerField(
        default=0,
        verbose_name=_('سنوات الخبرة في الإقراء والتحفيظ')
    )

    # --- بيانات خاصة بالطالب ---
    guardian_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_('اسم ولي الأمر')
    )
    guardian_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('رقم هاتف ولي الأمر')
    )
    guardian_relation = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('صلة قرابة ولي الأمر')
    )
    current_memorization_level = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('المستوى القرآني المبدئي')
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الانضمام للنظام'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ آخر تحديث'))

    class Meta:
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمين')
        ordering = ['-date_joined']

    def __str__(self):
        full = self.get_full_name()
        return f"{full} ({self.get_role_display()})" if full else f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_teacher_role(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student_role(self):
        return self.role == self.Role.STUDENT

    @property
    def display_name(self):
        return self.get_full_name() or self.username
