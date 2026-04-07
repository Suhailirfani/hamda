from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .models import Course, AdmissionApplication, WhatsAppTemplate
from .forms import AdmissionApplicationForm, WhatsAppTemplateForm
import json
import urllib.parse

def index(request):
    return render(request, 'index.html')

def admission_form_view(request):
    """Public view to submit a new admission application"""
    if request.method == 'POST':
        form = AdmissionApplicationForm(request.POST)
        if form.is_valid():
            application = form.save()
            return redirect('admission_success', app_no=application.application_number)
    else:
        form = AdmissionApplicationForm()

    # Pass courses mapping for the dependent dropdown via JS
    courses = list(Course.objects.values('id', 'name', 'section_id'))
    courses_json = json.dumps(courses)
        
    return render(request, 'academy/admission_form.html', {
        'form': form,
        'courses_json': courses_json
    })

def admission_success_view(request, app_no):
    """Public page shown after successfully submitting an application"""
    application = get_object_or_404(AdmissionApplication, application_number=app_no)
    return render(request, 'academy/admission_success.html', {
        'app_no': app_no,
        'application': application
    })

def admission_status_view(request):
    """Public page to check admission status using application number"""
    application = None
    searched = False
    
    if request.method == 'POST':
        app_number = request.POST.get('application_number', '').strip()
    else:
        app_number = request.GET.get('app_no', '').strip()
        
    if app_number:
        searched = True
        application = AdmissionApplication.objects.filter(application_number__iexact=app_number).first()
        if not application:
            messages.error(request, 'Application not found. Please check your application number.')
            
    return render(request, 'academy/admission_status.html', {
        'application': application,
        'searched': searched,
    })


# --- Authentication & Admin Panel Views ---
def custom_login(request):
    if request.user.is_authenticated:
        return redirect_user_based_on_role(request.user)
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect_user_based_on_role(user)
    else:
        form = AuthenticationForm()
    
    return render(request, 'academy/admin/login.html', {'form': form})

def custom_logout(request):
    auth_logout(request)
    return redirect('login')

def redirect_user_based_on_role(user):
    """Helper to route user to correct dashboard"""
    if user.is_superuser:
        return redirect('admin_dashboard')
    
    if hasattr(user, 'profile'):
        if user.profile.role in ['superadmin', 'admin', 'office_staff']:
            return redirect('admin_dashboard')
            
    return redirect('welcome_dashboard')

@login_required
def welcome_dashboard(request):
    """Placeholder dashboard for Teachers and Students"""
    return render(request, 'academy/admin/welcome.html')

@role_required(['superadmin', 'admin', 'office_staff'])
def admin_dashboard_view(request):
    """List View for Applications"""
    status_filter = request.GET.get('status', '')
    query = AdmissionApplication.objects.all()
    
    if status_filter:
        query = query.filter(status=status_filter)
        
    template_obj = WhatsAppTemplate.objects.first()
    template_text = template_obj.message_template if template_obj else "Hi {name}, your application for {course} has been received. Your application number is {app_no}."
    
    # Inject WhatsApp message and URL into each application
    for app in query:
        app_course = app.course.name if app.course else ""
        try:
            msg = template_text.format(name=app.name, course=app_course, app_no=app.application_number or "")
        except KeyError:
            # Fallback if the user wrote an invalid tag in the template
            msg = template_text.replace("{name}", app.name).replace("{course}", app_course).replace("{app_no}", app.application_number or "")
            
        app.whatsapp_url = f"https://wa.me/91{app.phone.replace('+91', '').replace(' ', '')}?text={urllib.parse.quote(msg)}"
        
    return render(request, 'academy/admin/dashboard.html', {
        'applications': query,
        'status_filter': status_filter
    })

@role_required(['superadmin', 'admin', 'office_staff'])
def enquiry_update_view(request, app_id):
    """Detail & Edit View for Applications"""
    application = get_object_or_404(AdmissionApplication, pk=app_id)
    if request.method == 'POST':
        form = AdmissionApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application updated successfully.')
            return redirect('admin_dashboard')
    else:
        form = AdmissionApplicationForm(instance=application)
        
    return render(request, 'academy/admin/enquiry_edit.html', {
        'form': form,
        'application': application
    })

@role_required(['superadmin', 'admin'])
def enquiry_delete_view(request, app_id):
    """Delete View (Restricted roles only)"""
    application = get_object_or_404(AdmissionApplication, pk=app_id)
    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Application deleted successfully.')
    return redirect('admin_dashboard')

@role_required(['superadmin', 'admin', 'office_staff'])
def enquiry_update_status_view(request, app_id):
    """View to update 'status' directly from the dashboard table"""
    application = get_object_or_404(AdmissionApplication, pk=app_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(AdmissionApplication.STATUS_CHOICES):
            application.status = new_status
            application.save()
            messages.success(request, f'Status for application {application.application_number} updated to {new_status}.')
        else:
            messages.error(request, 'Invalid status selected.')
    return redirect('admin_dashboard')

@role_required(['superadmin', 'admin'])
def whatsapp_template_edit_view(request):
    """View to edit WhatsApp default message"""
    template_obj = WhatsAppTemplate.objects.first()
    if not template_obj:
        template_obj = WhatsAppTemplate()
        
    if request.method == 'POST':
        form = WhatsAppTemplateForm(request.POST, instance=template_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'WhatsApp template updated successfully.')
            return redirect('admin_dashboard')
    else:
        form = WhatsAppTemplateForm(instance=template_obj)
        
    return render(request, 'academy/admin/whatsapp_template_edit.html', {
        'form': form
    })
