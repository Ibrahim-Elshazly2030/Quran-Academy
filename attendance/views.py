import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_date

from accounts.models import User
from accounts.decorators import staff_or_teacher_required, admin_required
from academy.models import Halaqah, EnrollmentHistory
from .models import AttendanceRecord

@login_required
@staff_or_teacher_required
def halaqah_attendance_sheet(request, halaqah_id):
    """
    كشف تسجيل الحضور والغياب والتأخير لحلقة قرآنية محددة.
    يتحقق من أن الشيخ يملك صلاحية فقط على هذه الحلقة.
    يدعم:
    - حاضر
    - غائب بعذر
    - غائب بدون عذر
    - متأخر بعذر (مع تسجيل الدقائق)
    - متأخر بدون عذر (مع تسجيل الدقائق)
    - مستأذن
    """
    halaqah = get_object_or_404(Halaqah, id=halaqah_id)

    # التحقق الأمني من الصلاحية
    if not request.user.is_admin_role and halaqah.teacher != request.user:
        messages.error(request, 'عفواً، لا تملك صلاحية تسجيل الحضور لحلقة شيخ آخر.')
        raise PermissionDenied

    # تحديد تاريخ الجلسة
    date_str = request.GET.get('date') or request.POST.get('session_date')
    if date_str:
        selected_date = parse_date(date_str) or timezone.now().date()
    else:
        selected_date = timezone.now().date()

    active_enrollments = halaqah.enrollments.filter(
        status=EnrollmentHistory.Status.ACTIVE
    ).select_related('student').order_by('student__first_name')

    if request.method == 'POST':
        saved_count = 0
        for enr in active_enrollments:
            student = enr.student
            status_val = request.POST.get(f'status_{student.id}', AttendanceRecord.Status.PRESENT)
            delay_val = request.POST.get(f'delay_{student.id}', '0')
            notes_val = request.POST.get(f'notes_{student.id}', '').strip()

            try:
                delay_minutes = max(0, int(delay_val)) if delay_val else 0
            except ValueError:
                delay_minutes = 0

            # تحديث أو إنشاء سجل الحضور لهذا الطالب في هذا اليوم
            AttendanceRecord.objects.update_or_create(
                student=student,
                halaqah=halaqah,
                date=selected_date,
                defaults={
                    'sheikh': request.user if request.user.is_teacher_role else halaqah.teacher,
                    'status': status_val,
                    'delay_minutes': delay_minutes,
                    'notes': notes_val
                }
            )
            saved_count += 1

        messages.success(
            request,
            f"تم حفظ كشف الحضور والغياب بنجاح ليوم {selected_date} لعدد {saved_count} طالب في حلقة '{halaqah.name}'."
        )
        # العودة لنفس التاريخ
        return redirect(f"{request.path}?date={selected_date}")

    # استرجاع السجلات المسجلة مسبقاً لهذا التاريخ إن وجدت
    existing_records = {
        rec.student_id: rec
        for rec in AttendanceRecord.objects.filter(halaqah=halaqah, date=selected_date)
    }

    # دمج الطلاب مع سجلاتهم
    students_rows = []
    for enr in active_enrollments:
        record = existing_records.get(enr.student.id)
        students_rows.append({
            'student': enr.student,
            'current_status': record.status if record else AttendanceRecord.Status.PRESENT,
            'delay_minutes': record.delay_minutes if record else 0,
            'notes': record.notes if record else '',
            'has_recorded': record is not None,
        })

    # إحصائيات سريعة لكشف اليوم
    status_choices = AttendanceRecord.Status.choices

    return render(request, 'attendance/sheet.html', {
        'halaqah': halaqah,
        'selected_date': selected_date,
        'today': timezone.now().date(),
        'students_rows': students_rows,
        'status_choices': status_choices,
        'total_students': len(students_rows),
    })


@login_required
@admin_required
def admin_attendance_overview(request):
    """استعراض الإدارة لسجلات الحضور والغياب على مستوى كافة الحلقات والشيوخ"""
    date_str = request.GET.get('date', '')
    halaqah_id = request.GET.get('halaqah', '')
    status_filter = request.GET.get('status', '')

    records = AttendanceRecord.objects.select_related(
        'student', 'halaqah', 'sheikh'
    ).order_by('-date', 'halaqah__name', 'student__first_name')

    if date_str:
        d = parse_date(date_str)
        if d:
            records = records.filter(date=d)
    
    if halaqah_id:
        records = records.filter(halaqah_id=halaqah_id)

    if status_filter:
        records = records.filter(status=status_filter)

    halaqat = Halaqah.objects.filter(is_active=True).order_by('name')

    return render(request, 'attendance/admin_overview.html', {
        'records': records[:100],
        'halaqat': halaqat,
        'selected_date': date_str,
        'selected_halaqah': halaqah_id,
        'selected_status': status_filter,
        'status_choices': AttendanceRecord.Status.choices,
    })
