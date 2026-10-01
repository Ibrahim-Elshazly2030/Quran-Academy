from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'role', 'phone_number', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'gender')
    search_fields = ('username', 'first_name', 'last_name', 'national_id', 'phone_number', 'guardian_name')
    fieldsets = UserAdmin.fieldsets + (
        ('معلومات المنظومة القرآنية', {
            'fields': (
                'role', 'gender', 'national_id', 'phone_number', 'birth_date', 'address', 'avatar'
            )
        }),
        ('بيانات الشيخ / المعلم', {
            'fields': (
                'ijazah_details', 'qualification', 'years_of_experience'
            )
        }),
        ('بيانات الطالب وولي الأمر', {
            'fields': (
                'guardian_name', 'guardian_phone', 'guardian_relation', 'current_memorization_level'
            )
        }),
    )
