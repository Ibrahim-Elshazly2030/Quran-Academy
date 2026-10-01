from django.contrib import admin
from .models import Surah, Halaqah, EnrollmentHistory

@admin.register(Surah)
class SurahAdmin(admin.ModelAdmin):
    list_display = ('number', 'name_arabic', 'ayah_count', 'revelation_place', 'start_page', 'juz_number')
    search_fields = ('name_arabic', 'number')
    list_filter = ('revelation_place', 'juz_number')
    ordering = ['number']

class EnrollmentInline(admin.TabularInline):
    model = EnrollmentHistory
    extra = 1
    fk_name = 'halaqah'
    fields = ('student', 'status', 'start_date', 'end_date', 'notes')

@admin.register(Halaqah)
class HalaqahAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'category', 'time_period', 'days_schedule', 'is_active', 'current_students_count')
    list_filter = ('category', 'time_period', 'is_active')
    search_fields = ('name', 'teacher__first_name', 'teacher__last_name', 'room_location')
    inlines = [EnrollmentInline]

@admin.register(EnrollmentHistory)
class EnrollmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('student', 'halaqah', 'assigned_sheikh', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'halaqah', 'assigned_sheikh', 'start_date')
    search_fields = ('student__first_name', 'student__last_name', 'student__username', 'halaqah__name')
