from django.urls import path
from . import views

app_name = 'evaluations'

urlpatterns = [
    # تقييم التسميع لحلقة الشيخ
    path('halaqah/<int:halaqah_id>/', views.halaqah_evaluate_view, name='halaqah_evaluate'),
    # إدارة معايير التقييم للإدارة
    path('criteria/', views.admin_criteria_manage, name='admin_criteria'),
]
