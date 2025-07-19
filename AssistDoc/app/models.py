from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('doctor', 'Doctor'),
        ('hospital_admin', 'Hospital Admin'),
        ('super_admin', 'App Super Administrator'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='doctor')
    professional_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    speciality = models.CharField(max_length=100, null=True, blank=True)
    hospitals = models.ManyToManyField('Hospital', related_name='doctors')
    
    # --- FIX for fields.E304: Explicitly define groups and user_permissions ---
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions'
            'granted to each of their groups.'
        ),
        # Unique related_name for your custom User model's groups
        related_name="custom_user_groups",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=('user permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        # Unique related_name for your custom User model's user_permissions
        related_name="custom_user_permissions",
        related_query_name="custom_user",
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

class Hospital(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    hospital_code = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Hospital"
        verbose_name_plural = "Hospitals"

class Patient(models.Model):
    unique_platform_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    age = models.PositiveIntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.unique_platform_id})"

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_records')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    ENTRY_TYPE_CHOICES = (
        ('consultation', 'Consultation'),
        ('lab_exam', 'Lab Exam'),
        ('medical_imaging', 'Medical Imaging'),
        ('prescription', 'Prescription'),
        ('diagnosis', 'Diagnosis'),
        ('clinical_note', 'Clinical Note'),
    )
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES)
    textual_content = models.TextField(blank=True, null=True)
    attached_file = models.FileField(upload_to='medical_records/', blank=True, null=True)
    diagnosis_code = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Record for {self.patient.last_name} ({self.entry_type}) - {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Medical Record"
        verbose_name_plural = "Medical Records"
        ordering = ['-created_at']

class AIRecommendation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='ai_recommendations')
    medical_record_entry = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='generated_recommendations')
    consulting_doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_recommendations')
    generated_at = models.DateTimeField(auto_now_add=True)

    RECOMMENDATION_TYPE_CHOICES = (
        ('differential_diagnosis', 'Differential Diagnosis'),
        ('suggested_treatment_plan', 'Suggested Treatment Plan'),
        ('additional_exams', 'Additional Exams'),
        ('risk_prevention', 'Risk Prevention'),
        ('follow_up', 'Follow-up Recommendation'),
    )
    recommendation_type = models.CharField(max_length=50, choices=RECOMMENDATION_TYPE_CHOICES)
    recommendation_content = models.TextField()
    recommendation_accepted = models.BooleanField(default=False)
    doctor_comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"AI Recommendation for {self.patient.last_name} ({self.recommendation_type})"

    class Meta:
        verbose_name = "AI Recommendation"
        verbose_name_plural = "AI Recommendations"
        ordering = ['-generated_at']