from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('', views.index, name='index'),
    path('apply/', views.admission_form_view, name='admission_form'),
    path('apply/success/<str:app_no>/', views.admission_success_view, name='admission_success'),
    path('apply/status/', views.admission_status_view, name='admission_status'),
    
    # Authentication
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Admin Panel
    path('panel/', views.admin_dashboard_view, name='admin_dashboard'),
    path('panel/enquiry/<int:app_id>/edit/', views.enquiry_update_view, name='enquiry_edit'),
    path('panel/enquiry/<int:app_id>/status/', views.enquiry_update_status_view, name='enquiry_update_status'),
    path('panel/enquiry/<int:app_id>/delete/', views.enquiry_delete_view, name='enquiry_delete'),
    
    # Settings
    path('panel/settings/whatsapp/', views.whatsapp_template_edit_view, name='whatsapp_template_edit'),
    
    # Welcome fallback
    path('welcome/', views.welcome_dashboard, name='welcome_dashboard'),
]
