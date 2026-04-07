from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class AcademicYear(models.Model):
    """Academic session year, e.g., '2024-2025'"""
    name = models.CharField(max_length=50, help_text="e.g., '2024-2025'")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False, help_text="Is this the active academic year?")

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            # Ensure no other academic year is active
            AcademicYear.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

class Section(models.Model):
    """Section/Department of the institution, e.g., Degree, Diploma, HSS"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Order for display sorting")

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Course(models.Model):
    """Course/Division like B.A Afzal Ul Ulama, Commerce, Science, etc."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='courses')

    class Meta:
        ordering = ['section__order', 'name']
        unique_together = [['name', 'section']]

    def __str__(self):
        return f"{self.name} ({self.section.name})"

class AdmissionApplication(models.Model):
    """Model to store prospective student admission applications"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Received', 'Application Received'),
        ('Token Generated', 'Token Generated'),
        ('Enrolled', 'Enrolled'),
        ('Rejected', 'Rejected'),
    ]

    STREAM_CHOICES = [
        ('NEET', 'NEET'),
        ('KEAM', 'KEAM'),
        ('JEE', 'JEE'),
        ('CUET', 'CUET'),
        ('Others', 'Others'),
    ]

    name = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    address = models.TextField()
    aadhar_number = models.CharField(max_length=20, blank=True, verbose_name="Aadhar Number")
    
    phone = models.CharField(max_length=20, verbose_name="Mobile Number")
    is_whatsapp_number = models.BooleanField(default=False, verbose_name="Is this number using WhatsApp?")
    
    fathers_name = models.CharField(max_length=100, blank=True, verbose_name="Father's/Guardian's Name")
    
    # Interested Course fields
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, verbose_name="Section/Department")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, verbose_name="Interested Course")
    
    # Entrance Coaching fields
    interested_in_entrance_coaching = models.BooleanField(default=False, verbose_name="Interested in Entrance Coaching?")
    preferred_stream = models.CharField(max_length=50, choices=STREAM_CHOICES, blank=True, null=True)
    other_stream = models.CharField(max_length=100, blank=True, verbose_name="If Others, specify")

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True)
    application_number = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="Auto-generated application number")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    token_number = models.IntegerField(null=True, blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Admission Applications'

    def __str__(self):
        return f"{self.application_number or 'Pending'} - {self.name} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.application_number:
            # Auto-generate application number
            today = timezone.now().date()
            year_str = today.strftime('%y') # e.g. '26'
            month_str = today.strftime('%m') # e.g. '04'
            
            section_letter = 'X' # Default if no section
            if self.section and self.section.name:
                section_letter = self.section.name.strip()[0].upper()
                
            prefix = f"{section_letter}{year_str}{month_str}"
            
            # Count applications starting with this prefix
            count = AdmissionApplication.objects.filter(application_number__startswith=prefix).count()
            
            count_str = f"{count + 1:02d}"
            self.application_number = f"{prefix}{count_str}"
            
            # Auto-assign active academic year if not present
            if not self.academic_year:
                active_year = AcademicYear.objects.filter(is_active=True).first()
                if active_year:
                    self.academic_year = active_year
            
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('superadmin', 'Superadmin'),
        ('admin', 'Admin'),
        ('office_staff', 'Office Staff'),
        ('teacher', 'Teacher'),
        ('student', 'Student/Parent'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'superadmin' if instance.is_superuser else 'student'
        UserProfile.objects.create(user=instance, role=role)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class WhatsAppTemplate(models.Model):
    """Singleton model to store the WhatsApp template message"""
    message_template = models.TextField(
        default="Hi {name}, your application for {course} has been received. Your application number is {app_no}.",
        help_text="Use {name}, {course}, and {app_no} as placeholders."
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "WhatsApp Message Template"
