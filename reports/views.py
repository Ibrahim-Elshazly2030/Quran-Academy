from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db.models import Q
from accounts.models import User
from accounts.decorators import staff_or_teacher_required, admin_required
from academy.models import Halaqah, EnrollmentHistory
from .services import (
    get_student_comprehensive_data,
    get_sheikh_comprehensive_data,
    get_academy_overview_stats
)

@login_required
def student_comprehensive_report(request, student_id):
    """
    التقرير التاريخي الشامل والمستوفي للطالب:
    - يعرض كامل تاريخ الطالب
    - جميع المجموعات التي انضم لها وتواريخ انتقاله
    - جميع الشيوخ الذين أشرفوا عليه
    - إحصائيات الحضور والغياب والتأخير بعذر وبدون عذر
    - سجل التسميع والتقييمات والدرجات والملاحظات
    صلاحيات العرض:
    - الإدارة
    - الشيخ الذي يدرس الطالب حالياً أو درسه سابقاً
    - الطالب نفسه للاطلاع على سجله وإنجازه
    """
    student = get_object_or_404(User, id=student_id, role=User.Role.STUDENT)

    # التحقق من الصلاحيات
    if not request.user.is_admin_role:
        if request.user.is_teacher_role:
            has_taught = EnrollmentHistory.objects.filter(
                student=student
            ).filter(
                Q(assigned_sheikh=request.user) | Q(halaqah__teacher=request.user)
            ).exists()
            if not has_taught:
                messages.error(request, 'عفواً، لا يمكنك الاطلاع على تقرير طالب ليس مسجلاً في حلقاتك.')
                raise PermissionDenied
        elif request.user.id != student.id:
            messages.error(request, 'عفواً، لا يمكنك الاطلاع على تقرير هذا الطالب.')
            raise PermissionDenied

    data = get_student_comprehensive_data(student.id)
    if not data:
        messages.error(request, 'تعذر تحميل بيانات التقرير.')
        return redirect('accounts:dashboard_redirect')

    return render(request, 'reports/student_report.html', {
        'data': data,
        'student': student,
        'printable': request.GET.get('print') == 'true',
    })


@login_required
@staff_or_teacher_required
def sheikh_comprehensive_report(request, sheikh_id):
    """
    التقرير التاريخي الشامل للشيخ:
    - بيانات الشيخ وسند إجازاته
    - كافة الحلقات الحالية والسابقة
    - كافة الطلاب الذين درسهم عبر التاريخ والطلاب الحاليين
    - مؤشرات الحضور والتسميع
    صلاحيات العرض:
    - الإدارة
    - الشيخ نفسه
    """
    sheikh = get_object_or_404(User, id=sheikh_id, role=User.Role.TEACHER)

    # التحقق من الصلاحية: الشيخ نفسه أو الإدارة
    if not request.user.is_admin_role and request.user.id != sheikh.id:
        messages.error(request, 'عفواً، لا يمكنك الاطلاع على تقرير هذا الشيخ.')
        raise PermissionDenied

    data = get_sheikh_comprehensive_data(sheikh.id)
    if not data:
        messages.error(request, 'تعذر تحميل بيانات تقرير الشيخ.')
        return redirect('accounts:dashboard_redirect')

    return render(request, 'reports/sheikh_report.html', {
        'data': data,
        'sheikh': sheikh,
        'printable': request.GET.get('print') == 'true',
    })


@login_required
@admin_required
def academy_overview_report(request):
    """التقرير التحليلي الشامل للمنظومة القرآنية"""
    stats = get_academy_overview_stats()
    
    # جميع الحلقات مع مؤشرات تفصيلية
    halaqat = Halaqah.objects.select_related('teacher').order_by('name')

    # جميع الشيوخ
    sheikhs = User.objects.filter(role=User.Role.TEACHER, is_active=True).order_by('first_name')

    return render(request, 'reports/academy_overview.html', {
        'stats': stats,
        'halaqat': halaqat,
        'sheikhs': sheikhs,
    })
