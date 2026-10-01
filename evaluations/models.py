from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from academy.models import Halaqah, Surah

class EvaluationCriterion(models.Model):
    """معايير جدول التقييم التي تحددها الإدارة لتنظيم تقييم الشيوخ للطلاب"""
    name = models.CharField(max_length=150, verbose_name=_('اسم المعيار'))
    code = models.CharField(max_length=50, unique=True, verbose_name=_('رمز المعيار الإداري'))
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=10.0, verbose_name=_('الدرجة العظمى'))
    description = models.TextField(blank=True, verbose_name=_('إرشادات احتساب المعيار للشيخ'))
    is_active = models.BooleanField(default=True, verbose_name=_('مفعل في جداول التقييم'))
    sort_order = models.PositiveIntegerField(default=1, verbose_name=_('ترتيب الظهور'))

    class Meta:
        verbose_name = _('معيار تقييم')
        verbose_name_plural = _('معايير وجداول التقييم')
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.name} (الدرجة القصوى: {self.max_score})"


class RecitationSession(models.Model):
    """
    جلسة التسميع والتقييم القرآني اليومية/الدورية لكل طالب في حلقته
    """
    class RecitationType(models.TextChoices):
        NEW_MEMORIZATION = 'new_memorization', _('حفظ جديد (الورد اليومي)')
        NEAR_REVISION = 'near_revision', _('مراجعة صغرى (المحفوظ القريب)')
        FAR_REVISION = 'far_revision', _('مراجعة كبرى (المحفوظ القديم)')
        TILAWAH_TAJWEED = 'tilawah_tajweed', _('تلاوة تصحيح وضبط تجويد')
        MATN = 'matn', _('متون التجويد والقراءات')
        EXAM = 'exam', _('اختبار تقييمي / ترقية')

    class RatingGrade(models.TextChoices):
        EXCELLENT_PLUS = 'A+', _('ممتاز مرتفع (متقن جداً)')
        EXCELLENT = 'A', _('ممتاز (متقن)')
        VERY_GOOD = 'B', _('جيد جداً')
        GOOD = 'C', _('جيد')
        ACCEPTABLE = 'D', _('مقبول')
        NEEDS_REPETITION = 'F', _('يحتاج إعادة تسميع')

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recitations',
        limit_choices_to={'role': 'student'},
        verbose_name=_('الطالب')
    )
    halaqah = models.ForeignKey(
        Halaqah,
        on_delete=models.CASCADE,
        related_name='recitations',
        verbose_name=_('الحلقة / المجموعة')
    )
    sheikh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluated_recitations',
        limit_choices_to={'role': 'teacher'},
        verbose_name=_('الشيخ المقيم')
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name=_('تاريخ التسميع')
    )
    recitation_type = models.CharField(
        max_length=30,
        choices=RecitationType.choices,
        default=RecitationType.NEW_MEMORIZATION,
        verbose_name=_('نوع التسميع')
    )

    # تفاصيل الموضع القرآني
    surah_from = models.ForeignKey(
        Surah,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recitation_start_surahs',
        verbose_name=_('من سورة')
    )
    ayah_from = models.PositiveIntegerField(
        default=1,
        verbose_name=_('من آية')
    )
    surah_to = models.ForeignKey(
        Surah,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recitation_end_surahs',
        verbose_name=_('إلى سورة')
    )
    ayah_to = models.PositiveIntegerField(
        default=1,
        verbose_name=_('إلى آية')
    )
    pages_completed = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=1.0,
        verbose_name=_('عدد الصفحات المنجزة')
    )

    # درجات جدول التقييم
    score_memorization = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.0,
        verbose_name=_('درجة الحفظ والضبط (من 10)')
    )
    score_tajweed = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.0,
        verbose_name=_('درجة التجويد ومخارج الحروف (من 10)')
    )
    score_fluency = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5.0,
        verbose_name=_('درجة الترتيل والوقف والابتداء (من 5)')
    )
    score_discipline = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5.0,
        verbose_name=_('درجة الانضباط والآداب (من 5)')
    )
    total_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.0,
        verbose_name=_('المجموع الكلي للتقييم (من 30)')
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=100.0,
        verbose_name=_('النسبة المئوية (%)')
    )
    rating_grade = models.CharField(
        max_length=5,
        choices=RatingGrade.choices,
        default=RatingGrade.EXCELLENT,
        verbose_name=_('التقدير العام')
    )

    # إحصائيات الأخطاء والتردد
    hesitations_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('عدد الترددات والتعثرات')
    )
    major_mistakes = models.PositiveIntegerField(
        default=0,
        verbose_name=_('اللحن الجلي (تغيير حرف/حركة)')
    )
    minor_mistakes = models.PositiveIntegerField(
        default=0,
        verbose_name=_('اللحن الخفي (أحكام الغنن والمدود)')
    )

    # التوجيه والمقرر القادم
    sheikh_notes = models.TextField(
        blank=True,
        verbose_name=_('ملاحظات وتوجيهات الشيخ للطالب')
    )
    next_assignment = models.CharField(
        max_length=250,
        blank=True,
        verbose_name=_('الواجب القرآني والمقرر للجلسة القادمة')
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('وقت الرصد'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التعديل'))

    class Meta:
        verbose_name = _('جلسة تسميع وتقييم')
        verbose_name_plural = _('جلسات التسميع والتقييمات')
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.student.display_name} - {self.get_recitation_type_display()} - {self.rating_grade} ({self.date})"

    def calculate_scores(self):
        # حساب المجموع الكلي (من 30)
        self.total_score = float(self.score_memorization) + float(self.score_tajweed) + float(self.score_fluency) + float(self.score_discipline)
        self.percentage = round((self.total_score / 30.0) * 100, 1)

        # تحديد التقدير التلقائي
        if self.percentage >= 95:
            self.rating_grade = self.RatingGrade.EXCELLENT_PLUS
        elif self.percentage >= 90:
            self.rating_grade = self.RatingGrade.EXCELLENT
        elif self.percentage >= 80:
            self.rating_grade = self.RatingGrade.VERY_GOOD
        elif self.percentage >= 70:
            self.rating_grade = self.RatingGrade.GOOD
        elif self.percentage >= 60:
            self.rating_grade = self.RatingGrade.ACCEPTABLE
        else:
            self.rating_grade = self.RatingGrade.NEEDS_REPETITION

    def save(self, *args, **kwargs):
        self.calculate_scores()
        super().save(*args, **kwargs)

    @property
    def location_display(self):
        from_s = f"سورة {self.surah_from.name_arabic} (آية {self.ayah_from})" if self.surah_from else ""
        to_s = f"إلى سورة {self.surah_to.name_arabic} (آية {self.ayah_to})" if self.surah_to else ""
        if from_s and to_s:
            return f"{from_s} {to_s}"
        return from_s or to_s or "غير محدد"
