from django import forms
from .models import AdmissionApplication

class AdmissionApplicationForm(forms.ModelForm):
    class Meta:
        model = AdmissionApplication
        fields = ['name', 'dob', 'address', 'aadhar_number', 'phone', 'is_whatsapp_number', 'fathers_name', 'section', 'course', 'interested_in_entrance_coaching', 'preferred_stream', 'other_stream']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'House Name, Place, PO, District'}),
            'aadhar_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Aadhar number'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mobile number'}),
            'is_whatsapp_number': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fathers_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter father's/guardian's name"}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'interested_in_entrance_coaching': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'preferred_stream': forms.Select(attrs={'class': 'form-select'}),
            'other_stream': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'If Others, specify'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The course list will be loaded dynamically via Javascript, so we can set its queryset to empty initially if needed
        # but to satisfy validation, we keep the original queryset or filter based on post data
        if 'section' in self.data:
            try:
                section_id = int(self.data.get('section'))
                from .models import Course
                self.fields['course'].queryset = Course.objects.filter(section_id=section_id).order_by('name')
            except (ValueError, TypeError):
                pass

from .models import WhatsAppTemplate

class WhatsAppTemplateForm(forms.ModelForm):
    class Meta:
        model = WhatsAppTemplate
        fields = ['message_template']
        widgets = {
            'message_template': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
