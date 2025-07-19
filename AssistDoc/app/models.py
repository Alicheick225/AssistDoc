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
    social_security_number = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    antecedents = models.TextField(blank=True, null=True)  # Medical history
    allergies = models.TextField(blank=True, null=True)  # Allergies    

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.social_security_number})"

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"



class Symptom(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Symptom"
        verbose_name_plural = "Symptoms"

class Consultation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='consultations_hospital')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='performed_consultations')
    consultation_date = models.DateTimeField(auto_now_add=True)
    consultation_reason = models.TextField()
    clinical_exam = models.TextField(blank=True, null=True)
    initial_diagnosis = models.TextField(blank=True, null=True)
    tension = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Tension artérielle
    temperature = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)  # Température corporelle
    heart_rate = models.PositiveIntegerField(null=True, blank=True)  # Fréquence cardiaque    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Taille du patient
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Poids du patient
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Taille du patient
    oxygen_saturation = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Saturation en oxygène
    symptoms = models.ManyToManyField(Symptom, related_name='consultations', blank=True)


    def __str__(self):
        return f"Consultation for {self.patient.last_name} on {self.consultation_date.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Consultation"
        verbose_name_plural = "Consultations"
        ordering = ['-consultation_date']


class Diagnostic(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='diagnostics')
    hopital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='diagnostics_hopital')
    medecin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='diagnostics_poses')
    
    date_diagnostic = models.DateTimeField(auto_now_add=True)
    
    # Lien optionnel vers la consultation qui a mené à ce diagnostic
    consultation = models.ForeignKey(Consultation, on_delete=models.SET_NULL, null=True, blank=True, related_name='diagnostics_associes')
    
    # Code de diagnostic (ex: CIM-10) et description
    code_cim = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField()
    
    # Statut du diagnostic (ex: provisoire, définitif, réfuté)
    STATUT_CHOICES = (
        ('provisoire', 'Provisoire'),
        ('definitif', 'Définitif'),
        ('refute', 'Réfuté'),
    )
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='provisoire')

    def __str__(self):
        return f"Diagnostic pour {self.patient.nom}: {self.description}"

    class Meta:
        verbose_name = "Diagnostic"
        verbose_name_plural = "Diagnostics"
        ordering = ['-date_diagnostic']



class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    hopital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='prescriptions_hopital')
    medecin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='prescriptions_faites')
    
    date_prescription = models.DateTimeField(auto_now_add=True)
    
    # Lien optionnel vers la consultation ou le diagnostic qui a mené à cette prescription
    consultation = models.ForeignKey(Consultation, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescriptions_associees')
    diagnostic = models.ForeignKey(Diagnostic, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescriptions_associees')

    medicament = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequence = models.CharField(max_length=100)
    duree = models.CharField(max_length=100)
    instructions = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Prescription de {self.medicament} pour {self.patient.nom}"

    class Meta:
        verbose_name = "Prescription"
        verbose_name_plural = "Prescriptions"
        ordering = ['-date_prescription']


class ExamenLaboratoire(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='examens_laboratoire')
    hopital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='examens_laboratoire_hopital')
    medecin_prescripteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='examens_prescrits')
    
    date_demande = models.DateTimeField(auto_now_add=True)
    date_resultat = models.DateTimeField(null=True, blank=True)
    
    type_examen = models.CharField(max_length=100) # Ex: "Hémogramme", "Glycémie"
    resultats_textuels = models.TextField(blank=True, null=True) # Pour des résultats simples
    fichier_resultats = models.FileField(upload_to='lab_results/', blank=True, null=True) # Pour rapports PDF

    # Vous pouvez ajouter un champ pour les valeurs normales, unités, etc.

    def __str__(self):
        return f"Examen Labo {self.type_examen} pour {self.patient.nom}"

    class Meta:
        verbose_name = "Examen Laboratoire"
        verbose_name_plural = "Examens Laboratoire"
        ordering = ['-date_resultat', '-date_demande']


class ImagerieMedicale(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='imageries_medicales')
    hopital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='imageries_medicales_hopital')
    medecin_prescripteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='imageries_prescrites')
    
    date_examen = models.DateTimeField(auto_now_add=True)
    type_imagerie = models.CharField(max_length=100, choices=[('radio', 'Radiographie'), ('irm', 'IRM'), ('scanner', 'Scanner'), ('echo', 'Échographie')])
    rapport_textuel = models.TextField(blank=True, null=True)
    fichier_imagerie = models.FileField(upload_to='medical_imaging/', blank=True, null=True) # Pour les images DICOM ou JPG/PNG
    
    def __str__(self):
        return f"{self.type_imagerie} pour {self.patient.nom}"

    class Meta:
        verbose_name = "Imagerie Médicale"
        verbose_name_plural = "Imageries Médicales"
        ordering = ['-date_examen']


class AIRecommendation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='ai_recommendations')
    
    # Liens optionnels vers les événements spécifiques qui ont pu générer la recommandation
    consultation_source = models.ForeignKey(Consultation, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_recos_from_consult')
    diagnostic_source = models.ForeignKey(Diagnostic, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_recos_from_diag')
    examen_labo_source = models.ForeignKey(ExamenLaboratoire, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_recos_from_lab')
    
    # Le médecin à qui la recommandation a été présentée (pour traçabilité)
    medecin_consultant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_ai_recommendations')
    
    generated_at = models.DateTimeField(auto_now_add=True)

    RECOMMENDATION_TYPE_CHOICES = (
        ('diagnostic_diff', 'Diagnostic Différentiel'),
        ('suggested_treatment_plan', 'Suggested Treatment Plan'),
        ('additional_exams', 'Additional Exams'),
        ('risk_prevention', 'Risk Prevention'),
        ('follow_up', 'Follow-up Recommendation'),
        ('info_medicale_pertinente', 'Information Médicale Pertinente') # Ajout possible
    )
    recommendation_type = models.CharField(max_length=50, choices=RECOMMENDATION_TYPE_CHOICES)
    recommendation_content = models.TextField()
    
    # Métadonnées de la recommandation (ex: score de confiance de l'IA)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Score de confiance de l'IA pour cette recommandation (0-100%)")

    recommendation_accepted = models.BooleanField(default=False)
    doctor_comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Recommandation IA pour {self.patient.nom} ({self.recommendation_type})"

    class Meta:
        verbose_name = "Recommandation IA"
        verbose_name_plural = "Recommandations IA"
        ordering = ['-generated_at']