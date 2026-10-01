from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # التقرير التاريخي المستوفي للطالب
    path('student/<int:student_id>/', views.student_comprehensive_report, name='student_report'),
    # التقرير التاريخي الشامل للشيخ
    path('sheikh/<int:sheikh_id>/', views.sheikh_comprehensive_report, name='sheikh_report'),
    # التقرير العام للمنظومة
    path('overview/', views.academy_overview_report, name='academy_overview'),
]
