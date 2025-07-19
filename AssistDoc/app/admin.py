from django.contrib import admin
from .models import User, Hospital, Patient

@admin.register(User)
class UserAdmin(admin.ModelAdmin):      
    list_display = ('username', 'email', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')
    
@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):  
    list_display = ('name',)
    search_fields = ('name',)
    
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):  
    list_display = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name')
    
