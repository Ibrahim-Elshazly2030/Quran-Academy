from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import CustomLoginForm
from .models import User

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"مرحباً بك فضيلة {user.display_name} في منظومة صرح القرآن.")
            return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')
    else:
        form = CustomLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('accounts:login')


@login_required
def dashboard_redirect(request):
    """توجيه المستخدم تلقائياً حسب نوع حسابه وصلاحياته"""
    user = request.user
    if user.is_admin_role:
        return redirect('academy:admin_dashboard')
    elif user.is_teacher_role:
        return redirect('academy:sheikh_dashboard')
    elif user.is_student_role:
        return redirect('reports:student_report', student_id=user.id)
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """الملف الشخصي وتغيير كلمة المرور"""
    if request.method == 'POST' and 'change_password' in request.POST:
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'تم تحديث كلمة المرور بنجاح.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء في نموذج تغيير كلمة المرور.')
    else:
        password_form = PasswordChangeForm(request.user)

    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'password_form': password_form,
    })
