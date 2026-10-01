from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_admin_role:
            messages.error(request, 'عفواً، هذه الصفحة مخصصة فقط لإدارة الأكاديمية.')
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def teacher_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_teacher_role:
            messages.error(request, 'عفواً، هذه الصفحة مخصصة لمشايخ ومعلمي الحلقات.')
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_student_role:
            messages.error(request, 'عفواً، هذه الصفحة مخصصة للطلاب فقط.')
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def staff_or_teacher_required(view_func):
    """يسمح للشيخ وللإدارة بالدخول معاً"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_admin_role or request.user.is_teacher_role):
            messages.error(request, 'ليس لديك صلاحية الوصول إلى هذه الصفحة.')
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view
