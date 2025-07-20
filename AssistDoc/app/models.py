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
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    address = models.TextField(null=True, blank=True)
    diseases = models.TextField(blank=True, null=True)  # Medical conditions
    surgeries = models.TextField(blank=True, null=True)  # Past surgeries*
    vaccines = models.TextField(blank=True, null=True)  # Vaccination history
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    allergies = models.TextField(blank=True, null=True)  # Allergies
    actual_medecines = models.TextField(blank=True, null=True)  # Current medications    

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
    heart_rate = models.PositiveIntegerField(null=True, blank=True)  # Fréquence cardiaque
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Poids du patient
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Taille du patient
    oxygen_saturation = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Saturation en oxygène
    symptoms = models.ManyToManyField(Symptom, related_name='consultations', blank=True)
    is_validated = models.BooleanField(default=False)  # Statut de validation de la consultation
    gemini_recommendations = models.JSONField(blank=True, null=True)  # Stockage des recommandations Gemini


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
        return f"Diagnostic pour {self.patient.first_name} {self.patient.last_name}: {self.description}"

    class Meta:
        verbose_name = "Diagnostic"
        verbose_name_plural = "Diagnostics"
        ordering = ['-date_diagnostic']


class PrescriptionFeedback(models.Model):
    """
    Modèle pour capturer le feedback des médecins sur les prescriptions générées par l'IA
    """
    FEEDBACK_CHOICES = (
        ('validee_directement', 'Validée directement'),
        ('modifiee', 'Modifiée avant validation'),
        ('annulee', 'Annulée/Rejetée'),
    )
    
    EFFICACITE_CHOICES = (
        ('tres_efficace', 'Très efficace'),
        ('efficace', 'Efficace'),
        ('moderement_efficace', 'Modérément efficace'),
        ('peu_efficace', 'Peu efficace'),
        ('inefficace', 'Inefficace'),
        ('non_evalue', 'Non évalué'),
    )
    
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name='feedback')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescription_feedbacks')
    
    # Type de feedback principal
    feedback_type = models.CharField(max_length=30, choices=FEEDBACK_CHOICES)
    
    # Détails des modifications si applicable
    modifications_effectuees = models.TextField(blank=True, null=True, help_text="Décrivez les modifications apportées à la prescription originale")
    raison_modification = models.TextField(blank=True, null=True, help_text="Pourquoi ces modifications étaient nécessaires")
    
    # Évaluation de l'efficacité du traitement (renseigné lors du suivi)
    efficacite_traitement = models.CharField(max_length=20, choices=EFFICACITE_CHOICES, default='non_evalue')
    effets_secondaires_observes = models.TextField(blank=True, null=True)
    duree_guerison = models.PositiveIntegerField(blank=True, null=True, help_text="Durée de guérison en jours")
    
    # Retour patient (optionnel)
    satisfaction_patient = models.PositiveIntegerField(blank=True, null=True, help_text="Score de satisfaction de 1 à 10")
    commentaires_patient = models.TextField(blank=True, null=True)
    
    # Évaluation de la qualité de l'IA
    pertinence_diagnostic = models.PositiveIntegerField(default=5, help_text="Pertinence du diagnostic IA de 1 à 10")
    pertinence_prescription = models.PositiveIntegerField(default=5, help_text="Pertinence de la prescription IA de 1 à 10")
    commentaires_medecin = models.TextField(blank=True, null=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    suivi_complete = models.BooleanField(default=False, help_text="Le suivi post-traitement est-il terminé")
    
    class Meta:
        verbose_name = "Feedback Prescription"
        verbose_name_plural = "Feedbacks Prescriptions"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Feedback {self.feedback_type} - {self.consultation.patient.get_full_name()} - {self.date_creation.strftime('%Y-%m-%d')}"


class AILearningData(models.Model):
    """
    Modèle pour stocker les données d'apprentissage pour améliorer l'IA
    """
    # Données d'entrée (anonymisées)
    age_patient = models.PositiveIntegerField()
    sexe_patient = models.CharField(max_length=10)
    symptomes_principaux = models.TextField()
    antecedents_medicaux = models.TextField()
    signes_vitaux = models.JSONField()
    
    # Prescription originale de l'IA
    prescription_ia_originale = models.JSONField()
    diagnostic_ia_original = models.TextField()
    
    # Correction/validation du médecin
    prescription_finale_medecin = models.JSONField()
    diagnostic_final_medecin = models.TextField()
    
    # Résultat du traitement
    efficacite_traitement = models.CharField(max_length=20, choices=PrescriptionFeedback.EFFICACITE_CHOICES)
    effets_secondaires = models.TextField(blank=True, null=True)
    duree_guerison = models.PositiveIntegerField(blank=True, null=True)
    
    # Scores de qualité
    score_pertinence_diagnostic = models.PositiveIntegerField()
    score_pertinence_prescription = models.PositiveIntegerField()
    
    # Métadonnées pour l'apprentissage
    feedback_source = models.ForeignKey(PrescriptionFeedback, on_delete=models.CASCADE, related_name='learning_data')
    date_creation = models.DateTimeField(auto_now_add=True)
    utilise_pour_entrainement = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Données d'Apprentissage IA"
        verbose_name_plural = "Données d'Apprentissage IA"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Données apprentissage - Patient {self.age_patient}ans - {self.date_creation.strftime('%Y-%m-%d')}"


class IAPerformanceMetrics(models.Model):
    """
    Modèle pour suivre les métriques de performance de l'IA dans le temps
    """
    date_calcul = models.DateField(unique=True)
    
    # Métriques générales
    total_prescriptions = models.PositiveIntegerField(default=0)
    prescriptions_validees_directement = models.PositiveIntegerField(default=0)
    prescriptions_modifiees = models.PositiveIntegerField(default=0)
    prescriptions_rejetees = models.PositiveIntegerField(default=0)
    
    # Taux de précision
    taux_validation_directe = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # %
    taux_modification = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # %
    taux_rejet = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # %
    
    # Scores moyens de qualité
    score_moyen_diagnostic = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    score_moyen_prescription = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    
    # Efficacité des traitements
    taux_efficacite_elevee = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    duree_moyenne_guerison = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    
    # Satisfaction
    satisfaction_moyenne_patients = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    satisfaction_moyenne_medecins = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    
    class Meta:
        verbose_name = "Métriques Performance IA"
        verbose_name_plural = "Métriques Performance IA"
        ordering = ['-date_calcul']
    
    def __str__(self):
        return f"Métriques IA - {self.date_calcul} - Validation directe: {self.taux_validation_directe}%"


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
        return f"Prescription de {self.medicament} pour {self.patient.first_name} {self.patient.last_name}"

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
        return f"Examen Labo {self.type_examen} pour {self.patient.first_name} {self.patient.last_name}"

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
        return f"{self.type_imagerie} pour {self.patient.first_name} {self.patient.last_name}"

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
        return f"Recommandation IA pour {self.patient.first_name} {self.patient.last_name} ({self.recommendation_type})"

    class Meta:
        verbose_name = "Recommandation IA"
        verbose_name_plural = "Recommandations IA"
        ordering = ['-generated_at']


class FeedbackPattern(models.Model):
    """
    Modèle pour stocker les patterns extraits des feedbacks
    Utilisé pour enrichir les prompts Gemini automatiquement
    """
    PATTERN_TYPE_CHOICES = [
        ('frequent_modification', 'Modification Fréquente'),
        ('frequent_rejection', 'Rejet Fréquent'),
        ('good_practice', 'Bonne Pratique'),
        ('dosage_preference', 'Préférence de Dosage'),
        ('diagnostic_error', 'Erreur de Diagnostic'),
        ('prescription_error', 'Erreur de Prescription'),
    ]
    
    pattern_type = models.CharField(max_length=50, choices=PATTERN_TYPE_CHOICES)
    description = models.TextField(help_text="Description du pattern identifié")
    frequency = models.PositiveIntegerField(default=1, help_text="Nombre d'occurrences")
    confidence_score = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.0,
        help_text="Score de confiance du pattern (0.0 à 1.0)"
    )
    
    # Métadonnées
    first_occurrence = models.DateTimeField(auto_now_add=True)
    last_occurrence = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Pattern actif pour enrichissement prompt")
    
    # Relations optionnelles
    related_feedbacks = models.ManyToManyField(
        'PrescriptionFeedback', 
        blank=True,
        help_text="Feedbacks sources de ce pattern"
    )
    
    class Meta:
        verbose_name = "Pattern de Feedback"
        verbose_name_plural = "Patterns de Feedback"
        ordering = ['-frequency', '-confidence_score', '-last_occurrence']
        unique_together = ['pattern_type', 'description']
    
    def __str__(self):
        return f"{self.get_pattern_type_display()}: {self.description[:50]}..."
    
    @property
    def reliability_level(self):
        """Retourne le niveau de fiabilité du pattern"""
        if self.frequency >= 10 and self.confidence_score >= 0.7:
            return "Élevé"
        elif self.frequency >= 5 and self.confidence_score >= 0.5:
            return "Moyen"
        elif self.frequency >= 2 and self.confidence_score >= 0.3:
            return "Faible"
        else:
            return "Très faible"