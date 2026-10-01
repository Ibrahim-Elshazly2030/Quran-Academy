from django.contrib import admin
from .models import EvaluationCriterion, RecitationSession

@admin.register(EvaluationCriterion)
class EvaluationCriterionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'max_score', 'is_active', 'sort_order')
    list_editable = ('max_score', 'is_active', 'sort_order')

@admin.register(RecitationSession)
class RecitationSessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'halaqah', 'sheikh', 'date', 'recitation_type', 'location_display', 'total_score', 'rating_grade')
    list_filter = ('recitation_type', 'rating_grade', 'date', 'halaqah', 'sheikh')
    search_fields = ('student__first_name', 'student__last_name', 'sheikh_notes', 'next_assignment')
    date_hierarchy = 'date'
