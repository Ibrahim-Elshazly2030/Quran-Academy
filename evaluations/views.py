from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone

from accounts.models import User
from accounts.decorators import staff_or_teacher_required, admin_required
from academy.models import Halaqah, EnrollmentHistory, Surah
from .models import EvaluationCriterion, RecitationSession
from .forms import RecitationSessionForm

@login_required
@staff_or_teacher_required
def halaqah_evaluate_view(request, halaqah_id):
    """
    تسجيل جلسة تقييم وتسميع لطالب في حلقة الشيخ وفق جداول التقييم المعتمدة.
    يتحقق من أن الشيخ يملك صلاحية فقط على طلاب هذه الحلقة.
    """
    halaqah = get_object_or_404(Halaqah, id=halaqah_id)

    # التحقق الأمني: الشيخ يرى ويقيم فقط طلاب حلقته
    if not request.user.is_admin_role and halaqah.teacher != request.user:
        messages.error(request, 'عفواً، لا يمكنك إجراء تقييم لحلقة شيخ آخر.')
        raise PermissionDenied

    # الطالب المحدد مسبقاً من الرابط إن وجد
    preselected_student_id = request.GET.get('student')
    initial_data = {'date': timezone.now().date()}
    if preselected_student_id:
        initial_data['student'] = preselected_student_id

    if request.method == 'POST':
        form = RecitationSessionForm(halaqah=halaqah, data=request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.halaqah = halaqah
            session.sheikh = request.user if request.user.is_teacher_role else halaqah.teacher
            session.save()

            messages.success(
                request,
                f"تم حفظ تقييم الطالب {session.student.display_name} بنجاح: "
                f"المجموع: {session.total_score}/30 ({session.percentage}%) - التقدير: {session.get_rating_grade_display()}."
            )
            return redirect('evaluations:halaqah_evaluate', halaqah_id=halaqah.id)
        else:
            messages.error(request, 'يرجى مراجعة وتصحيح الحقول في استمارة التقييم.')
    else:
        form = RecitationSessionForm(halaqah=halaqah, initial=initial_data)

    # أحدث التقييمات في هذه الحلقة
    recent_sessions = RecitationSession.objects.filter(
        halaqah=halaqah
    ).select_related('student', 'sheikh', 'surah_from', 'surah_to').order_by('-date', '-created_at')[:15]

    # معايير التقييم الإدارية المعتمدة
    criteria = EvaluationCriterion.objects.filter(is_active=True).order_by('sort_order')

    active_students = halaqah.enrollments.filter(
        status=EnrollmentHistory.Status.ACTIVE
    ).select_related('student').order_by('student__first_name')

    return render(request, 'evaluations/evaluate.html', {
        'halaqah': halaqah,
        'form': form,
        'criteria': criteria,
        'recent_sessions': recent_sessions,
        'active_students': active_students,
        'preselected_student_id': preselected_student_id,
    })


@login_required
@admin_required
def admin_criteria_manage(request):
    """إدارة معايير وجداول التقييم من قبل الإدارة"""
    if request.method == 'POST' and 'update_criterion' in request.POST:
        criterion_id = request.POST.get('criterion_id')
        criterion = get_object_or_404(EvaluationCriterion, id=criterion_id)
        criterion.max_score = request.POST.get('max_score', criterion.max_score)
        criterion.description = request.POST.get('description', criterion.description)
        criterion.is_active = 'is_active' in request.POST
        criterion.save()
        messages.success(request, f"تم تحديث المعيار '{criterion.name}' بنجاح.")
        return redirect('evaluations:admin_criteria')

    criteria = EvaluationCriterion.objects.all().order_by('sort_order')
    return render(request, 'evaluations/admin_criteria.html', {
        'criteria': criteria,
    })
