from django import forms
from .models import AttendanceRecord

class AttendanceRecordForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['status', 'delay_minutes', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select attendance-status-select'}),
            'delay_minutes': forms.NumberInput(attrs={'class': 'form-control delay-input', 'min': '0', 'placeholder': 'بالدقائق'}),
            'notes': forms.TextInput(attrs={'class': 'form-control notes-input', 'placeholder': 'ملاحظات العذر / التنبيه'}),
        }
