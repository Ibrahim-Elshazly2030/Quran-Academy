from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from accounts.models import User
from accounts.decorators import admin_required, teacher_required, staff_or_teacher_required
from accounts.forms import SheikhForm, StudentForm
from .models import Halaqah, EnrollmentHistory, Surah
from .forms import HalaqahForm, StudentTransferForm, DirectEnrollmentForm
from .org_settings import OrganizationSettings
from .org_settings_form import OrganizationSettingsForm
from attendance.models import AttendanceRecord
from evaluations.models import RecitationSession
from reports.services import get_academy_overview_stats

# ==============================================================================
# لوحة تحكم الإدارة وإدارة الشيوخ والطلاب والمجموعات
# ==============================================================================

@login_required
@admin_required
def admin_dashboard(request):
    """اللوحة الرئيسية للإدارة العليا لمتابعة كافة الشيوخ والطلاب والحلقات"""
    stats = get_academy_overview_stats()
    
    # قائمة الحلقات النشطة مع أعداد الطلاب
    halaqat = Halaqah.objects.select_related('teacher').annotate(
        students_count=Count('enrollments', filter=Q(enrollments__status=EnrollmentHistory.Status.ACTIVE))
    ).order_by('name')

    # الشيوخ النشطون
    sheikhs = User.objects.filter(role=User.Role.TEACHER, is_active=True).annotate(
        groups_count=Count('taught_halaqat', filter=Q(taught_halaqat__is_active=True))
    )[:6]

    # أحدث الأنشطة والتسميعات
    recent_recitations = RecitationSession.objects.select_related(
        'student', 'halaqah', 'sheikh', 'surah_from', 'surah_to'
    ).order_by('-date', '-created_at')[:8]

    # أحدث سجلات الحضور
    today = timezone.now().date()
    today_attendance = AttendanceRecord.objects.filter(date=today).select_related('student', 'halaqah', 'sheikh')[:10]

    return render(request, 'academy/admin_dashboard.html', {
        'stats': stats,
        'halaqat': halaqat,
        'sheikhs': sheikhs,
        'recent_recitations': recent_recitations,
        'today_attendance': today_attendance,
    })


# --- إدارة الشيوخ ---

@login_required
@admin_required
def sheikh_list(request):
    """عرض قائمة الشيوخ والمعلمين ومتابعة أداء مجموعاتهم"""
    query = request.GET.get('q', '')
    sheikhs = User.objects.filter(role=User.Role.TEACHER).annotate(
        active_groups=Count('taught_halaqat', filter=Q(taught_halaqat__is_active=True)),
        total_evaluations=Count('evaluated_recitations')
    ).order_by('-is_active', 'first_name')

    if query:
        sheikhs = sheikhs.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query) |
            Q(phone_number__icontains=query)
        )

    return render(request, 'academy/sheikh_list.html', {
        'sheikhs': sheikhs,
        'query': query,
    })


@login_required
@admin_required
def sheikh_add(request):
    """إضافة شيخ / معلم جديد للمنظومة"""
    if request.method == 'POST':
        form = SheikhForm(request.POST)
        if form.is_valid():
            sheikh = form.save()
            messages.success(request, f"تمت إضافة فضيلة الشيخ {sheikh.display_name} بنجاح.")
            return redirect('academy:sheikh_list')
        else:
            messages.error(request, 'يرجى مراجعة بيانات الشيخ المدخلة.')
    else:
        form = SheikhForm()

    return render(request, 'academy/sheikh_form.html', {
        'form': form,
        'title': 'إضافة شيخ ومعلم جديد',
        'is_edit': False
    })


@login_required
@admin_required
def sheikh_edit(request, sheikh_id):
    """تعديل بيانات الشيخ"""
    sheikh = get_object_or_404(User, id=sheikh_id, role=User.Role.TEACHER)
    if request.method == 'POST':
        form = SheikhForm(request.POST, instance=sheikh)
        if form.is_valid():
            form.save()
            messages.success(request, f"تم تحديث بيانات الشيخ {sheikh.display_name} بنجاح.")
            return redirect('academy:sheikh_list')
        else:
            messages.error(request, 'يرجى مراجعة البيانات المدخلة.')
    else:
        form = SheikhForm(instance=sheikh)

    return render(request, 'academy/sheikh_form.html', {
        'form': form,
        'title': f'تعديل ملف فضيلة الشيخ {sheikh.display_name}',
        'sheikh': sheikh,
        'is_edit': True
    })


# --- إدارة الحلقات والمجموعات ---

@login_required
@admin_required
def halaqah_list(request):
    """عرض كافة الحلقات والمجموعات القرآنية"""
    halaqat = Halaqah.objects.select_related('teacher').annotate(
        active_students=Count('enrollments', filter=Q(enrollments__status=EnrollmentHistory.Status.ACTIVE))
    ).order_by('-is_active', 'name')

    return render(request, 'academy/halaqah_list.html', {'halaqat': halaqat})


@login_required
@admin_required
def halaqah_add(request):
    """إنشاء حلقة جديدة وتعيين الشيخ المسؤول"""
    if request.method == 'POST':
        form = HalaqahForm(request.POST)
        if form.is_valid():
            halaqah = form.save()
            messages.success(request, f"تم إنشاء الحلقة '{halaqah.name}' بنجاح.")
            return redirect('academy:halaqah_list')
    else:
        form = HalaqahForm()

    return render(request, 'academy/halaqah_form.html', {
        'form': form,
        'title': 'إنشاء حلقة قرآنية جديدة',
        'is_edit': False
    })


@login_required
@admin_required
def halaqah_edit(request, halaqah_id):
    """تعديل بيانات الحلقة أو تغيير الشيخ"""
    halaqah = get_object_or_404(Halaqah, id=halaqah_id)
    if request.method == 'POST':
        form = HalaqahForm(request.POST, instance=halaqah)
        if form.is_valid():
            form.save()
            messages.success(request, f"تم تحديث الحلقة '{halaqah.name}' بنجاح.")
            return redirect('academy:halaqah_detail', halaqah_id=halaqah.id)
    else:
        form = HalaqahForm(instance=halaqah)

    return render(request, 'academy/halaqah_form.html', {
        'form': form,
        'title': f'تعديل حلقة: {halaqah.name}',
        'halaqah': halaqah,
        'is_edit': True
    })


@login_required
@staff_or_teacher_required
def halaqah_detail(request, halaqah_id):
    """تفاصيل الحلقة والطلاب المقيدين بها وسجلاتها"""
    halaqah = get_object_or_404(Halaqah.objects.select_related('teacher'), id=halaqah_id)

    # التحقق من الصلاحيات: الشيخ يرى فقط حلقته، الإدارة ترى كل الحلقات
    if not request.user.is_admin_role and halaqah.teacher != request.user:
        messages.error(request, 'غير مصرح لك باستعراض بيانات هذه الحلقة.')
        raise PermissionDenied

    active_enrollments = halaqah.enrollments.filter(
        status=EnrollmentHistory.Status.ACTIVE
    ).select_related('student').order_by('student__first_name')

    historical_enrollments = halaqah.enrollments.exclude(
        status=EnrollmentHistory.Status.ACTIVE
    ).select_related('student').order_by('-end_date')

    # إحصائيات حضور الحلقة
    today = timezone.now().date()
    today_records = AttendanceRecord.objects.filter(halaqah=halaqah, date=today)
    today_marked_student_ids = set(today_records.values_list('student_id', flat=True))

    enroll_form = DirectEnrollmentForm()

    return render(request, 'academy/halaqah_detail.html', {
        'halaqah': halaqah,
        'active_enrollments': active_enrollments,
        'historical_enrollments': historical_enrollments,
        'today': today,
        'today_marked_count': len(today_marked_student_ids),
        'enroll_form': enroll_form,
    })


@login_required
@admin_required
def halaqah_enroll_student(request, halaqah_id):
    """إلحاق طالب موجود بحلقة معينة"""
    halaqah = get_object_or_404(Halaqah, id=halaqah_id)
    if request.method == 'POST':
        form = DirectEnrollmentForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            notes = form.cleaned_data['notes']

            # التحقق مما إذا كان الطالب مسجلاً بنشاط في أي حلقة
            active_enr = EnrollmentHistory.objects.filter(student=student, status=EnrollmentHistory.Status.ACTIVE).first()
            if active_enr:
                if active_enr.halaqah == halaqah:
                    messages.warning(request, f"الطالب {student.display_name} مسجل بالفعل في هذه الحلقة!")
                    return redirect('academy:halaqah_detail', halaqah_id=halaqah.id)
                else:
                    # تحويل تلقائي مع توثيق الانتقال
                    active_enr.status = EnrollmentHistory.Status.TRANSFERRED
                    active_enr.end_date = timezone.now().date()
                    active_enr.notes += f" | نُقل إدارياً إلى {halaqah.name}"
                    active_enr.save()

            EnrollmentHistory.objects.create(
                student=student,
                halaqah=halaqah,
                assigned_sheikh=halaqah.teacher,
                status=EnrollmentHistory.Status.ACTIVE,
                start_date=timezone.now().date(),
                notes=notes,
                created_by=request.user
            )
            messages.success(request, f"تم إلحاق الطالب {student.display_name} بحلقة '{halaqah.name}' بنجاح.")

    return redirect('academy:halaqah_detail', halaqah_id=halaqah.id)


# --- إدارة الطلاب وسجل الانتقالات التاريخي الكامل ---

@login_required
@admin_required
def student_list(request):
    """استعراض الطلاب وحلقاتهم وشيوخهم المشرفين"""
    query = request.GET.get('q', '')
    students = User.objects.filter(role=User.Role.STUDENT).order_by('-date_joined')

    if query:
        students = students.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query) |
            Q(guardian_name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(national_id__icontains=query)
        )

    # إرفاق الحلقة الحالية والشيخ الحالي لكل طالب
    students_with_meta = []
    for s in students:
        active_enr = s.enrollment_history.filter(status=EnrollmentHistory.Status.ACTIVE).select_related('halaqah', 'assigned_sheikh').first()
        students_with_meta.append({
            'user': s,
            'current_halaqah': active_enr.halaqah if active_enr else None,
            'current_sheikh': active_enr.assigned_sheikh or (active_enr.halaqah.teacher if active_enr and active_enr.halaqah else None),
            'enrolled_at': active_enr.start_date if active_enr else None,
        })

    return render(request, 'academy/student_list.html', {
        'students_with_meta': students_with_meta,
        'query': query,
    })


@login_required
@admin_required
def student_add(request):
    """تسجيل طالب جديد وإلحاقه بحلقة وشيخ"""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        initial_halaqah_id = request.POST.get('initial_halaqah')
        if form.is_valid():
            student = form.save()
            if initial_halaqah_id:
                halaqah = Halaqah.objects.filter(id=initial_halaqah_id).first()
                if halaqah:
                    EnrollmentHistory.objects.create(
                        student=student,
                        halaqah=halaqah,
                        assigned_sheikh=halaqah.teacher,
                        status=EnrollmentHistory.Status.ACTIVE,
                        start_date=timezone.now().date(),
                        notes="التسجيل المبدئي للطالب بالمنظومة",
                        created_by=request.user
                    )
            messages.success(request, f"تم تسجيل الطالب {student.display_name} بنجاح.")
            return redirect('academy:student_list')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء في بيانات الطالب.')
    else:
        form = StudentForm()

    halaqat = Halaqah.objects.filter(is_active=True)
    return render(request, 'academy/student_form.html', {
        'form': form,
        'halaqat': halaqat,
        'title': 'تسجيل طالب جديد بالمنظومة',
        'is_edit': False
    })


@login_required
@admin_required
def student_edit(request, student_id):
    """تعديل بيانات الطالب"""
    student = get_object_or_404(User, id=student_id, role=User.Role.STUDENT)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"تم تحديث بيانات الطالب {student.display_name} بنجاح.")
            return redirect('academy:student_list')
        else:
            messages.error(request, 'يرجى مراجعة الأخطاء في النموذج.')
    else:
        form = StudentForm(instance=student)

    return render(request, 'academy/student_form.html', {
        'form': form,
        'student': student,
        'title': f'تعديل بيانات الطالب: {student.display_name}',
        'is_edit': True
    })


@login_required
@admin_required
def student_transfer(request, student_id):
    """
    نقل طالب من حلقة إلى أخرى مع توثيق الأرشيف التاريخي الكامل
    (الشيخ السابق، الحلقة السابقة، التاريخ، سبب النقل)
    """
    student = get_object_or_404(User, id=student_id, role=User.Role.STUDENT)
    active_enr = student.enrollment_history.filter(status=EnrollmentHistory.Status.ACTIVE).select_related('halaqah', 'assigned_sheikh').first()

    if request.method == 'POST':
        form = StudentTransferForm(request.POST)
        if form.is_valid():
            new_halaqah = form.cleaned_data['new_halaqah']
            reason = form.cleaned_data['transfer_reason']
            today = timezone.now().date()

            if active_enr and active_enr.halaqah == new_halaqah:
                messages.warning(request, "الطالب مقيد بالفعل في نفس هذه الحلقة!")
                return redirect('academy:student_transfer', student_id=student.id)

            # إنهاء القيد السابق وتوثيق تاريخه
            if active_enr:
                active_enr.status = EnrollmentHistory.Status.TRANSFERRED
                active_enr.end_date = today
                active_enr.notes = (active_enr.notes or '') + f"\n[تاريخ النقل {today}]: {reason}"
                active_enr.save()

            # إنشاء القيد الجديد بالحلقة والشيخ الجديد
            EnrollmentHistory.objects.create(
                student=student,
                halaqah=new_halaqah,
                assigned_sheikh=new_halaqah.teacher,
                status=EnrollmentHistory.Status.ACTIVE,
                start_date=today,
                notes=f"نُقل من حلقة {active_enr.halaqah.name if active_enr else 'غير محددة'}. السبب: {reason}",
                created_by=request.user
            )

            messages.success(request, f"تم نقل الطالب {student.display_name} بنجاح إلى حلقة '{new_halaqah.name}' مع حفظ سجله التاريخي.")
            return redirect('reports:student_report', student_id=student.id)
    else:
        form = StudentTransferForm()

    return render(request, 'academy/student_transfer.html', {
        'student': student,
        'current_enrollment': active_enr,
        'form': form,
    })


# ==============================================================================
# بوابة الشيخ الخاصة (Sheikh Portal) - مع العزل التام للبيانات
# ==============================================================================

@login_required
@teacher_required
def sheikh_dashboard(request):
    """
    لوحة تحكم الشيخ الخاصة:
    - يرى فقط حلقاته وطلابه المعينين له
    - إجراءات سريعة لرصد الحضور وجلسات التسميع
    """
    sheikh = request.user
    
    # استرجاع حلقات هذا الشيخ فقط!
    my_halaqat = Halaqah.objects.filter(teacher=sheikh, is_active=True).annotate(
        students_count=Count('enrollments', filter=Q(enrollments__status=EnrollmentHistory.Status.ACTIVE))
    ).order_by('name')

    total_my_students = EnrollmentHistory.objects.filter(
        halaqah__in=my_halaqat,
        status=EnrollmentHistory.Status.ACTIVE
    ).count()

    today = timezone.now().date()

    # رصد حضور اليوم لحلقاته
    today_attendance_records = AttendanceRecord.objects.filter(
        halaqah__in=my_halaqat,
        date=today
    )
    today_marked_count = today_attendance_records.count()

    # تقييمات التسميع الأخيرة التي أجراها هذا الشيخ
    recent_evaluations = RecitationSession.objects.filter(
        sheikh=sheikh
    ).select_related('student', 'halaqah', 'surah_from', 'surah_to').order_by('-date', '-created_at')[:8]

    return render(request, 'academy/sheikh_dashboard.html', {
        'sheikh': sheikh,
        'my_halaqat': my_halaqat,
        'total_my_students': total_my_students,
        'today': today,
        'today_marked_count': today_marked_count,
        'recent_evaluations': recent_evaluations,
    })


@login_required
@teacher_required
def sheikh_halaqah_view(request, halaqah_id):
    """عرض تفاصيل حلقة الشيخ مع التحقق الأمني الصارم من الملكية"""
    halaqah = get_object_or_404(Halaqah, id=halaqah_id)
    
    # التحقق من أن هذا الشيخ هو المشرف على الحلقة حصراً
    if halaqah.teacher != request.user and not request.user.is_admin_role:
        messages.error(request, 'عفواً، لا يمكنك استعراض حلقة تابعة لشيخ آخر.')
        raise PermissionDenied

    active_enrollments = halaqah.enrollments.filter(
        status=EnrollmentHistory.Status.ACTIVE
    ).select_related('student').order_by('student__first_name')

    today = timezone.now().date()
    today_attendance = {
        rec.student_id: rec for rec in AttendanceRecord.objects.filter(halaqah=halaqah, date=today)
    }

    # آخر تسميع لكل طالب في الحلقة
    latest_recitations = {}
    for enr in active_enrollments:
        last_rec = RecitationSession.objects.filter(student=enr.student, halaqah=halaqah).order_by('-date', '-created_at').first()
        latest_recitations[enr.student_id] = last_rec

    students_cards = []
    for enr in active_enrollments:
        students_cards.append({
            'student': enr.student,
            'enrollment': enr,
            'today_attendance': today_attendance.get(enr.student.id),
            'latest_recitation': latest_recitations.get(enr.student.id),
        })

    return render(request, 'academy/sheikh_halaqah_view.html', {
        'halaqah': halaqah,
        'students_cards': students_cards,
        'today': today,
    })


# ==============================================================================
# إعدادات المنشأة / الأكاديمية القرآنية
# ==============================================================================

@login_required
@admin_required
def organization_settings(request):
    """
    شاشة إعدادات المنشأة:
    - تسجيل اسم المنشأة / الأكاديمية أو الدار القرآنية
    - رفع الشعار (Logo)
    - بيانات التواصل والعنوان والمسؤولين
    - هذه البيانات تظهر تلقائياً في كل الصفحات والتقارير الرسمية
    """
    org = OrganizationSettings.get_settings()

    if request.method == 'POST':
        form = OrganizationSettingsForm(request.POST, request.FILES, instance=org)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'تم حفظ بيانات المنشأة "{org.name}" بنجاح. ستظهر التحديثات فوراً في كافة الصفحات والتقارير.'
            )
            return redirect('academy:organization_settings')
        else:
            messages.error(request, 'يرجى مراجعة الأخطاء في نموذج إعدادات المنشأة.')
    else:
        form = OrganizationSettingsForm(instance=org)

    return render(request, 'academy/organization_settings.html', {
        'form': form,
        'org': org,
    })
