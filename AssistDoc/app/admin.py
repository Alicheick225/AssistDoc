from django.contrib import admin
from .models import User, Hospital, Doctor, Patient, Consultation, Diagnosis, Prescription

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):  
    list_display = ('first_name', 'last_name', 'phone_number', 'email')
    search_fields = ('first_name', 'last_name', 'email')
    
    
@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone_number')
    search_fields = ('name', 'address')
    
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'specialite', 'matricule_medecin')
    search_fields = ('first_name', 'last_name', 'specialite', 'matricule_medecin')
    
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):   
    list_display = ('first_name', 'last_name', 'date_naissance', 'numero_securite_sociale')
    search_fields = ('first_name', 'last_name', 'numero_securite_sociale')
    
@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'hospital', 'date_consultation')
    search_fields = ('patient__first_name', 'doctor__first_name', 'hospital__name')
    
@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ('consultation', 'description', 'date_diagnosis')
    search_fields = ('consultation__patient__first_name', 'description')
    
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('consultation',)
    search_fields = ('consultation__patient__first_name',)                                                                  