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

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class StaffUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(
        choices=[
            ('admin', 'Admin'),
            ('office_staff', 'Office Staff'),
            ('teacher', 'Teacher'),
            ('student', 'Student/Parent'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['first_name', 'last_name', 'email', 'role']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data['role']
            profile.save()
        return user
