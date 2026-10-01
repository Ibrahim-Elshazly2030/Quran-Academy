from django.urls import path
from . import views

app_name = 'academy'

urlpatterns = [
    # بوابة الإدارة العليا
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    
    # إدارة الشيوخ
    path('admin-panel/sheikhs/', views.sheikh_list, name='sheikh_list'),
    path('admin-panel/sheikhs/add/', views.sheikh_add, name='sheikh_add'),
    path('admin-panel/sheikhs/<int:sheikh_id>/edit/', views.sheikh_edit, name='sheikh_edit'),

    # إدارة الحلقات
    path('admin-panel/halaqat/', views.halaqah_list, name='halaqah_list'),
    path('admin-panel/halaqat/add/', views.halaqah_add, name='halaqah_add'),
    path('admin-panel/halaqat/<int:halaqah_id>/', views.halaqah_detail, name='halaqah_detail'),
    path('admin-panel/halaqat/<int:halaqah_id>/edit/', views.halaqah_edit, name='halaqah_edit'),
    path('admin-panel/halaqat/<int:halaqah_id>/enroll/', views.halaqah_enroll_student, name='halaqah_enroll_student'),

    # إدارة الطلاب وسجلات الانتقال
    path('admin-panel/students/', views.student_list, name='student_list'),
    path('admin-panel/students/add/', views.student_add, name='student_add'),
    path('admin-panel/students/<int:student_id>/edit/', views.student_edit, name='student_edit'),
    path('admin-panel/students/<int:student_id>/transfer/', views.student_transfer, name='student_transfer'),

    # بوابة الشيخ
    path('sheikh/', views.sheikh_dashboard, name='sheikh_dashboard'),
    path('sheikh/halaqah/<int:halaqah_id>/', views.sheikh_halaqah_view, name='sheikh_halaqah_view'),

    # إعدادات المنشأة
    path('admin-panel/organization/', views.organization_settings, name='organization_settings'),
]
