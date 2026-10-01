from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # كشف حضور الحلقة للشيخ والإدارة
    path('halaqah/<int:halaqah_id>/', views.halaqah_attendance_sheet, name='halaqah_attendance_sheet'),
    # النظرة العامة للإدارة
    path('admin-overview/', views.admin_attendance_overview, name='admin_attendance_overview'),
]
