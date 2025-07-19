from django.db import models

# Create your models here.

class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)


class Hospital(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.name

    
class Doctor(User):
    specialite = models.CharField(max_length=100)
    matricule_medecin = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.specialite}"
    

class Patient(User):
    date_naissance = models.DateField()
    adresse = models.CharField(max_length=255)
    numero_securite_sociale = models.CharField(max_length=15, unique=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.date_naissance}"
    
    
class Consultation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    date_consultation = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Consultation of {self.patient} with {self.doctor} on {self.date_consultation}"        
    

class Diagnosis(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    description = models.TextField()
    date_diagnosis = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnosis for {self.consultation} on {self.date_diagnosis}"    


class Prescription(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    medication_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    instructions = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Prescription for {self.medication_name} in {self.consultation}"        