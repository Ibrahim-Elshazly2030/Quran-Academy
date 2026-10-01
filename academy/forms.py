from django import forms
from .models import Halaqah, EnrollmentHistory
from accounts.models import User

class HalaqahForm(forms.ModelForm):
    class Meta:
        model = Halaqah
        fields = [
            'name', 'teacher', 'category', 'days_schedule',
            'time_period', 'time_detail', 'room_location',
            'max_students', 'is_active', 'description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: حلقة الإمام الشاطبي'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'days_schedule': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: السبت، الإثنين، الأربعاء'}),
            'time_period': forms.Select(attrs={'class': 'form-select'}),
            'time_detail': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: 4:30 م - 6:00 م'}),
            'room_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: القاعة الكبرى'}),
            'max_students': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(role=User.Role.TEACHER, is_active=True)
        self.fields['teacher'].empty_label = "-- اختر الشيخ المشرف على الحلقة --"


class StudentTransferForm(forms.Form):
    """نموذج نقل طالب من حلقة إلى أخرى مع توثيق السجل التاريخي الكامل"""
    new_halaqah = forms.ModelChoiceField(
        queryset=Halaqah.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الحلقة الجديدة المراد النقل إليها',
        empty_label='-- اختر الحلقة المستهدفة --'
    )
    transfer_reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'اذكر سبب النقل (مثلاً: إتمام مستوى الحفظ والترقية، تغيير المواعيد، توصية الشيخ...)'
        }),
        label='سبب النقل والتوصية الإدارية',
        required=True
    )


class DirectEnrollmentForm(forms.Form):
    """إلحاق طالب موجود بحلقة معينة"""
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Role.STUDENT, is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='اختر الطالب',
        empty_label='-- حدد الطالب --'
    )
    notes = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ملاحظات القيد'}),
        label='ملاحظات القيد المبدئي',
        required=False
    )
