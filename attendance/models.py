from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from academy.models import Halaqah

class AttendanceRecord(models.Model):
    """
    سجل الحضور والغياب والتأخير للطلاب في الحلقة القرآنية
    """
    class Status(models.TextChoices):
        PRESENT = 'present', _('حاضر')
        ABSENT_EXCUSED = 'absent_excused', _('غائب بعذر')
        ABSENT_UNEXCUSED = 'absent_unexcused', _('غائب بدون عذر')
        LATE_EXCUSED = 'late_excused', _('متأخر بعذر')
        LATE_UNEXCUSED = 'late_unexcused', _('متأخر بدون عذر')
        EXCUSED_LEAVE = 'excused_leave', _('مستأذن أثناء الحلقة')

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        limit_choices_to={'role': 'student'},
        verbose_name=_('الطالب')
    )
    halaqah = models.ForeignKey(
        Halaqah,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name=_('الحلقة / المجموعة')
    )
    sheikh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_attendances',
        limit_choices_to={'role': 'teacher'},
        verbose_name=_('الشيخ الراصد للحضور')
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name=_('تاريخ الجلسة')
    )
    status = models.CharField(
        max_length=25,
        choices=Status.choices,
        default=Status.PRESENT,
        verbose_name=_('حالة الحضور والغياب')
    )
    delay_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_('مدة التأخير بالدقائق (في حال التأخير)')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('سبب العذر / ملاحظات الشيخ')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('وقت الرصد'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التعديل'))

    class Meta:
        verbose_name = _('سجل حضور وغياب')
        verbose_name_plural = _('سجلات الحضور والغياب والتأخير')
        ordering = ['-date', 'student__first_name']
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'halaqah', 'date'],
                name='unique_student_halaqah_date_attendance'
            )
        ]

    def __str__(self):
        return f"{self.student.display_name} - {self.date} - {self.get_status_display()}"

    @property
    def is_positive_attendance(self):
        return self.status in [self.Status.PRESENT, self.Status.LATE_EXCUSED]

    @property
    def badge_class(self):
        mapping = {
            self.Status.PRESENT: 'badge-success',
            self.Status.ABSENT_EXCUSED: 'badge-warning',
            self.Status.ABSENT_UNEXCUSED: 'badge-danger',
            self.Status.LATE_EXCUSED: 'badge-info',
            self.Status.LATE_UNEXCUSED: 'badge-dark-warning',
            self.Status.EXCUSED_LEAVE: 'badge-secondary',
        }
        return mapping.get(self.status, 'badge-light')
