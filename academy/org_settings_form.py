from django import forms
from academy.org_settings import OrganizationSettings


class OrganizationSettingsForm(forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            'name', 'name_en', 'slogan', 'logo', 'logo_icon_letter',
            'phone_primary', 'phone_secondary', 'email', 'website',
            'address', 'city', 'country',
            'license_number', 'founding_year',
            'supervisor_name', 'supervisor_title',
            'scientific_director',
            'report_footer_quote', 'report_footer_note',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: مدرسة النور القرآنية، أكاديمية صرح القرآن...'
            }),
            'name_en': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional: Noor Quran Academy'
            }),
            'slogan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: المنظومة التعليمية لإدارة الحلقات والمدارس القرآنية'
            }),
            'logo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'logo_icon_letter': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '3',
                'placeholder': 'مثال: ق، ن، ص'
            }),
            'phone_primary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0501234567'
            }),
            'phone_secondary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم إضافي (اختياري)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'info@your-academy.com'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://your-academy.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'العنوان التفصيلي للمقر الرئيسي'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: الرياض، مكة المكرمة، جدة...'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'المملكة العربية السعودية'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم ترخيص وزارة التعليم أو الشؤون الدينية'
            }),
            'founding_year': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1445 هـ / 2024 م'
            }),
            'supervisor_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الاسم الكامل للمشرف العام أو المدير التنفيذي'
            }),
            'supervisor_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: مدير عام، رئيس مجلس الإدارة...'
            }),
            'scientific_director': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مدير الشؤون التعليمية والقرآنية'
            }),
            'report_footer_quote': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'آية قرآنية أو حديث شريف يظهر في ذيل التقارير'
            }),
            'report_footer_note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'ملاحظة ختامية اختيارية تظهر في ذيل التقارير الرسمية'
            }),
        }
