from django import forms
from .models import RecitationSession, EvaluationCriterion
from academy.models import Surah, Halaqah
from accounts.models import User

class RecitationSessionForm(forms.ModelForm):
    class Meta:
        model = RecitationSession
        fields = [
            'student', 'date', 'recitation_type',
            'surah_from', 'ayah_from', 'surah_to', 'ayah_to', 'pages_completed',
            'score_memorization', 'score_tajweed', 'score_fluency', 'score_discipline',
            'hesitations_count', 'major_mistakes', 'minor_mistakes',
            'sheikh_notes', 'next_assignment'
        ]
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select', 'id': 'student_select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'recitation_type': forms.Select(attrs={'class': 'form-select'}),
            'surah_from': forms.Select(attrs={'class': 'form-select select-surah'}),
            'ayah_from': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'surah_to': forms.Select(attrs={'class': 'form-select select-surah'}),
            'ayah_to': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'pages_completed': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0'}),

            'score_memorization': forms.NumberInput(attrs={'class': 'form-control score-field', 'step': '0.5', 'min': '0', 'max': '10'}),
            'score_tajweed': forms.NumberInput(attrs={'class': 'form-control score-field', 'step': '0.5', 'min': '0', 'max': '10'}),
            'score_fluency': forms.NumberInput(attrs={'class': 'form-control score-field', 'step': '0.5', 'min': '0', 'max': '5'}),
            'score_discipline': forms.NumberInput(attrs={'class': 'form-control score-field', 'step': '0.5', 'min': '0', 'max': '5'}),

            'hesitations_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'major_mistakes': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'minor_mistakes': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),

            'sheikh_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'توجيهات الشيخ وتشجيعه للطالب...'}),
            'next_assignment': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: سورة الكهف من 1 إلى 30 + مراجعة جزء عم'}),
        }

    def __init__(self, halaqah=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if halaqah:
            active_student_ids = halaqah.enrollments.filter(status='active').values_list('student_id', flat=True)
            self.fields['student'].queryset = User.objects.filter(id__in=active_student_ids)
        self.fields['student'].empty_label = "-- اختر الطالب من طلاب حلقتك --"
        self.fields['surah_from'].queryset = Surah.objects.all().order_by('number')
        self.fields['surah_to'].queryset = Surah.objects.all().order_by('number')
        self.fields['surah_from'].empty_label = "-- سورة البداية --"
        self.fields['surah_to'].empty_label = "-- سورة النهاية --"
