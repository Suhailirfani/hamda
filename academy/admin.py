from django.contrib import admin
from .models import AcademicYear, Section, Course, AdmissionApplication, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    search_fields = ('name',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'section')
    list_filter = ('section',)
    search_fields = ('name',)

@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_number', 'name', 'phone', 'course', 'status', 'created_at')
    list_filter = ('status', 'section', 'course', 'academic_year', 'interested_in_entrance_coaching', 'preferred_stream')
    search_fields = ('name', 'application_number', 'phone', 'aadhar_number', 'fathers_name')
    readonly_fields = ('application_number', 'created_at', 'updated_at')
