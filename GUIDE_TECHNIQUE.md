# 🔧 Guide Technique - Système d'Amélioration IA

## 📁 Structure des Fichiers Modifiés/Créés

### Modèles de Base de Données (`app/models.py`)

#### PrescriptionFeedback
```python
class PrescriptionFeedback(models.Model):
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name='feedback')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks_donnes')
    
    FEEDBACK_CHOICES = [
        ('validee_directement', 'Validée directement'),
        ('modifiee', 'Modifiée par le médecin'),
        ('annulee', 'Annulée/Rejetée'),
    ]
    feedback_type = models.CharField(max_length=30, choices=FEEDBACK_CHOICES, default='validee_directement')
    
    # Évaluation de la qualité de l'IA (1-10)
    pertinence_diagnostic = models.PositiveIntegerField(
        default=5, 
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pertinence_prescription = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    # Informations sur les modifications
    modifications_effectuees = models.TextField(blank=True, null=True)
    raison_modification = models.TextField(blank=True, null=True)
    
    # Suivi de l'efficacité du traitement
    EFFICACITE_CHOICES = [
        ('tres_efficace', 'Très efficace'),
        ('efficace', 'Efficace'),
        ('moderement_efficace', 'Modérément efficace'),
        ('peu_efficace', 'Peu efficace'),
        ('inefficace', 'Inefficace'),
        ('non_evalue', 'Non évalué'),
    ]
    efficacite_traitement = models.CharField(
        max_length=20, 
        choices=EFFICACITE_CHOICES, 
        default='non_evalue'
    )
    
    duree_guerison = models.PositiveIntegerField(blank=True, null=True, help_text="Durée en jours")
    effets_secondaires_observes = models.TextField(blank=True, null=True)
    satisfaction_patient = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    # Commentaires
    commentaires_patient = models.TextField(blank=True, null=True)
    commentaires_medecin = models.TextField(blank=True, null=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    suivi_complete = models.BooleanField(default=False)
```

#### AILearningData
```python
class AILearningData(models.Model):
    # Données patient anonymisées
    age_patient = models.PositiveIntegerField()
    sexe_patient = models.CharField(max_length=10)
    symptomes_principaux = models.TextField()
    antecedents_medicaux = models.JSONField(default=dict)
    signes_vitaux = models.JSONField(default=dict)
    allergies_patient = models.TextField(blank=True, null=True)
    
    # Prescriptions (IA vs médecin)
    prescription_ia_originale = models.JSONField()
    prescription_finale_medecin = models.JSONField()
    modifications_apportees = models.TextField(blank=True, null=True)
    
    # Résultats et efficacité
    efficacite_traitement = models.CharField(max_length=20)
    score_pertinence_diagnostic = models.PositiveIntegerField()
    score_pertinence_prescription = models.PositiveIntegerField()
    duree_guerison_jours = models.PositiveIntegerField(blank=True, null=True)
    satisfaction_patient = models.PositiveIntegerField(blank=True, null=True)
    
    # Métadonnées pour l'apprentissage automatique
    date_creation = models.DateTimeField(auto_now_add=True)
    utilise_pour_entrainement = models.BooleanField(default=False)
    cycle_entrainement = models.CharField(max_length=50, blank=True, null=True)
    feedback_source = models.ForeignKey(PrescriptionFeedback, on_delete=models.CASCADE)
```

#### IAPerformanceMetrics
```python
class IAPerformanceMetrics(models.Model):
    date_calcul = models.DateField(unique=True)
    
    # Statistiques générales
    total_prescriptions = models.PositiveIntegerField(default=0)
    prescriptions_validees_directement = models.PositiveIntegerField(default=0)
    prescriptions_modifiees = models.PositiveIntegerField(default=0)
    prescriptions_rejetees = models.PositiveIntegerField(default=0)
    
    # Taux de performance (en pourcentages)
    taux_validation_directe = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    taux_modification = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    taux_rejet = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Scores moyens de qualité
    score_moyen_diagnostic = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    score_moyen_prescription = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    
    # Métrics d'efficacité
    efficacite_moyenne_traitements = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    duree_moyenne_guerison = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    satisfaction_moyenne_patients = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    
    # Compteur de données d'apprentissage générées
    donnees_apprentissage_generees = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-date_calcul']
        verbose_name = "Métriques de Performance IA"
        verbose_name_plural = "Métriques de Performance IA"
```

---

### Interface d'Administration (`app/admin.py`)

#### PrescriptionFeedbackAdmin
```python
@admin.register(PrescriptionFeedback)
class PrescriptionFeedbackAdmin(admin.ModelAdmin):
    list_display = [
        'consultation', 'doctor', 'feedback_type', 'pertinence_diagnostic', 
        'pertinence_prescription', 'efficacite_traitement', 'date_creation', 'suivi_complete'
    ]
    list_filter = [
        'feedback_type', 'efficacite_traitement', 'suivi_complete', 'date_creation', 
        'pertinence_diagnostic', 'pertinence_prescription'
    ]
    search_fields = [
        'consultation__patient__first_name', 'consultation__patient__last_name',
        'doctor__username', 'doctor__first_name', 'doctor__last_name'
    ]
    date_hierarchy = 'date_creation'
    readonly_fields = ['date_creation', 'date_modification']
    
    fieldsets = (
        ('Information Générale', {
            'fields': ('consultation', 'doctor', 'feedback_type', 'date_creation', 'date_modification')
        }),
        ('Évaluation de l\'IA', {
            'fields': ('pertinence_diagnostic', 'pertinence_prescription'),
            'classes': ('collapse',)
        }),
        ('Modifications Apportées', {
            'fields': ('modifications_effectuees', 'raison_modification'),
            'classes': ('collapse',)
        }),
        ('Suivi du Traitement', {
            'fields': ('efficacite_traitement', 'duree_guerison', 'effets_secondaires_observes', 'satisfaction_patient'),
            'classes': ('collapse',)
        }),
        ('Commentaires', {
            'fields': ('commentaires_medecin', 'commentaires_patient'),
            'classes': ('collapse',)
        }),
        ('Statut', {
            'fields': ('suivi_complete',),
        }),
    )
```

#### IAPerformanceMetricsAdmin avec Analytics
```python
@admin.register(IAPerformanceMetrics)
class IAPerformanceMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'date_calcul', 'total_prescriptions', 'taux_validation_directe', 
        'taux_modification', 'taux_rejet', 'score_moyen_diagnostic', 
        'score_moyen_prescription', 'donnees_apprentissage_generees'
    ]
    list_filter = ['date_calcul']
    readonly_fields = [
        'date_calcul', 'total_prescriptions', 'prescriptions_validees_directement',
        'prescriptions_modifiees', 'prescriptions_rejetees', 'taux_validation_directe',
        'taux_modification', 'taux_rejet', 'score_moyen_diagnostic',
        'score_moyen_prescription', 'efficacite_moyenne_traitements',
        'duree_moyenne_guerison', 'satisfaction_moyenne_patients',
        'donnees_apprentissage_generees'
    ]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_site.admin_view(self.analytics_view), name='analytics'),
        ]
        return custom_urls + urls
    
    def analytics_view(self, request):
        # Récupérer les 30 derniers jours de métriques
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        metrics = IAPerformanceMetrics.objects.filter(
            date_calcul__gte=thirty_days_ago
        ).order_by('date_calcul')
        
        # Préparer les données pour Chart.js
        dates = [metric.date_calcul.strftime('%Y-%m-%d') for metric in metrics]
        validation_rates = [float(metric.taux_validation_directe) for metric in metrics]
        modification_rates = [float(metric.taux_modification) for metric in metrics]
        rejection_rates = [float(metric.taux_rejet) for metric in metrics]
        diagnostic_scores = [float(metric.score_moyen_diagnostic) for metric in metrics]
        prescription_scores = [float(metric.score_moyen_prescription) for metric in metrics]
        
        # Données pour les graphiques en donut
        latest_metric = metrics.last() if metrics.exists() else None
        feedback_distribution = {}
        efficacite_distribution = {}
        
        if latest_metric:
            feedback_distribution = {
                'Validées': latest_metric.prescriptions_validees_directement,
                'Modifiées': latest_metric.prescriptions_modifiees,
                'Rejetées': latest_metric.prescriptions_rejetees,
            }
            
            # Calculer la distribution d'efficacité
            efficacite_counts = PrescriptionFeedback.objects.values('efficacite_traitement').annotate(
                count=Count('id')
            ).order_by('efficacite_traitement')
            
            efficacite_distribution = {
                item['efficacite_traitement']: item['count'] 
                for item in efficacite_counts
            }
        
        context = {
            'title': 'Analytics IA - Tableau de Bord',
            'dates': json.dumps(dates),
            'validation_rates': json.dumps(validation_rates),
            'modification_rates': json.dumps(modification_rates),
            'rejection_rates': json.dumps(rejection_rates),
            'diagnostic_scores': json.dumps(diagnostic_scores),
            'prescription_scores': json.dumps(prescription_scores),
            'feedback_distribution': json.dumps(feedback_distribution),
            'efficacite_distribution': json.dumps(efficacite_distribution),
            'latest_metric': latest_metric,
            'total_feedbacks': PrescriptionFeedback.objects.count(),
            'total_learning_data': AILearningData.objects.count(),
            'learning_data_used': AILearningData.objects.filter(utilise_pour_entrainement=True).count(),
        }
        
        return render(request, 'admin/analytics.html', context)
```

---

### Vues Backend (`app/views.py`)

#### Fonction de feedback automatique
```python
def create_automatic_feedback(consultation, doctor, feedback_type, base_score=8):
    """
    Crée automatiquement un feedback lors des actions sur les prescriptions
    """
    from .models import PrescriptionFeedback
    
    feedback, created = PrescriptionFeedback.objects.get_or_create(
        consultation=consultation,
        doctor=doctor,
        defaults={
            'feedback_type': feedback_type,
            'pertinence_diagnostic': base_score,
            'pertinence_prescription': base_score,
            'commentaires_medecin': f'Feedback automatique - {feedback_type}'
        }
    )
    
    if not created:
        feedback.feedback_type = feedback_type
        feedback.save()
    
    return feedback
```

#### Vue de feedback détaillé
```python
@csrf_protect
@login_required
def donner_feedback(request, consultation_id):
    """
    Permet au médecin de donner un feedback détaillé sur une prescription IA
    """
    try:
        consultation = get_object_or_404(Consultation, id=consultation_id, doctor=request.user)
        
        # Récupérer ou créer le feedback
        from .models import PrescriptionFeedback
        feedback, created = PrescriptionFeedback.objects.get_or_create(
            consultation=consultation,
            doctor=request.user,
            defaults={
                'feedback_type': 'validee_directement',
                'pertinence_diagnostic': 5,
                'pertinence_prescription': 5
            }
        )
        
        if request.method == 'POST':
            # Mettre à jour le feedback avec les données du formulaire
            feedback.feedback_type = request.POST.get('feedback_type', feedback.feedback_type)
            feedback.modifications_effectuees = request.POST.get('modifications_effectuees', '')
            feedback.raison_modification = request.POST.get('raison_modification', '')
            feedback.efficacite_traitement = request.POST.get('efficacite_traitement', 'non_evalue')
            feedback.effets_secondaires_observes = request.POST.get('effets_secondaires_observes', '')
            
            # Convertir en entier les champs numériques
            try:
                feedback.duree_guerison = int(request.POST.get('duree_guerison', 0)) if request.POST.get('duree_guerison') else None
                feedback.satisfaction_patient = int(request.POST.get('satisfaction_patient', 0)) if request.POST.get('satisfaction_patient') else None
                feedback.pertinence_diagnostic = int(request.POST.get('pertinence_diagnostic', 5))
                feedback.pertinence_prescription = int(request.POST.get('pertinence_prescription', 5))
            except ValueError:
                messages.error(request, 'Valeurs numériques invalides.')
                return render(request, 'donner_feedback.html', {'consultation': consultation, 'feedback': feedback})
            
            feedback.commentaires_patient = request.POST.get('commentaires_patient', '')
            feedback.commentaires_medecin = request.POST.get('commentaires_medecin', '')
            feedback.suivi_complete = request.POST.get('suivi_complete') == 'on'
            
            feedback.save()
            
            messages.success(request, 'Feedback enregistré avec succès. Merci de contribuer à l\'amélioration de l\'IA!')
            return redirect('dashboard')
        
        # Affichage du formulaire
        context = {
            'consultation': consultation,
            'patient': consultation.patient,
            'feedback': feedback,
            'feedback_choices': PrescriptionFeedback.FEEDBACK_CHOICES,
            'efficacite_choices': PrescriptionFeedback.EFFICACITE_CHOICES,
        }
        return render(request, 'donner_feedback.html', context)
        
    except Exception as e:
        messages.error(request, f'Erreur lors du feedback: {str(e)}')
        return redirect('dashboard')
```

---

### Commande de Gestion (`app/management/commands/calculate_ai_metrics.py`)

```python
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import timedelta, datetime
from app.models import PrescriptionFeedback, IAPerformanceMetrics, AILearningData, Consultation


class Command(BaseCommand):
    help = 'Calcule les métriques de performance de l\'IA pour une date donnée'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date pour laquelle calculer les métriques (format: YYYY-MM-DD)',
        )

    def handle(self, *args, **options):
        # Déterminer la date pour laquelle calculer les métriques
        if options['date']:
            try:
                target_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Format de date invalide. Utilisez YYYY-MM-DD')
                )
                return
        else:
            target_date = timezone.now().date()

        self.stdout.write(f'Calcul des métriques pour le {target_date}...')

        # Récupérer tous les feedbacks pour cette date
        feedbacks = PrescriptionFeedback.objects.filter(
            date_creation__date=target_date
        )

        # Calculer les statistiques de base
        total_prescriptions = feedbacks.count()
        
        if total_prescriptions == 0:
            self.stdout.write(
                self.style.WARNING(f'Aucun feedback trouvé pour le {target_date}')
            )
            return

        # Compter par type de feedback
        validees_directement = feedbacks.filter(feedback_type='validee_directement').count()
        modifiees = feedbacks.filter(feedback_type='modifiee').count()
        rejetees = feedbacks.filter(feedback_type='annulee').count()

        # Calculer les taux (en pourcentages)
        taux_validation = (validees_directement / total_prescriptions) * 100
        taux_modification = (modifiees / total_prescriptions) * 100
        taux_rejet = (rejetees / total_prescriptions) * 100

        # Calculer les scores moyens
        scores_avg = feedbacks.aggregate(
            diagnostic_avg=Avg('pertinence_diagnostic'),
            prescription_avg=Avg('pertinence_prescription'),
            satisfaction_avg=Avg('satisfaction_patient')
        )

        # Calculer l'efficacité moyenne des traitements
        efficacite_mapping = {
            'tres_efficace': 5,
            'efficace': 4,
            'moderement_efficace': 3,
            'peu_efficace': 2,
            'inefficace': 1,
            'non_evalue': 0
        }
        
        efficacite_scores = []
        for feedback in feedbacks.filter(efficacite_traitement__isnull=False):
            score = efficacite_mapping.get(feedback.efficacite_traitement, 0)
            if score > 0:  # Exclure les "non_evalue"
                efficacite_scores.append(score)
        
        efficacite_moyenne = sum(efficacite_scores) / len(efficacite_scores) if efficacite_scores else 0

        # Calculer la durée moyenne de guérison
        durees_guerison = feedbacks.filter(
            duree_guerison__isnull=False
        ).values_list('duree_guerison', flat=True)
        
        duree_moyenne = sum(durees_guerison) / len(durees_guerison) if durees_guerison else None

        # Créer ou mettre à jour les métriques
        metrics, created = IAPerformanceMetrics.objects.update_or_create(
            date_calcul=target_date,
            defaults={
                'total_prescriptions': total_prescriptions,
                'prescriptions_validees_directement': validees_directement,
                'prescriptions_modifiees': modifiees,
                'prescriptions_rejetees': rejetees,
                'taux_validation_directe': round(taux_validation, 2),
                'taux_modification': round(taux_modification, 2),
                'taux_rejet': round(taux_rejet, 2),
                'score_moyen_diagnostic': round(scores_avg['diagnostic_avg'] or 0, 1),
                'score_moyen_prescription': round(scores_avg['prescription_avg'] or 0, 1),
                'efficacite_moyenne_traitements': round(efficacite_moyenne, 1),
                'duree_moyenne_guerison': round(duree_moyenne, 1) if duree_moyenne else None,
                'satisfaction_moyenne_patients': round(scores_avg['satisfaction_avg'] or 0, 1),
            }
        )

        # Générer des données d'apprentissage pour les feedbacks avec suivi terminé
        feedbacks_termines = feedbacks.filter(suivi_complete=True)
        donnees_generees = 0
        
        for feedback in feedbacks_termines:
            # Vérifier si des données d'apprentissage existent déjà
            if not AILearningData.objects.filter(feedback_source=feedback).exists():
                # Anonymiser et créer les données d'apprentissage
                self.create_learning_data(feedback)
                donnees_generees += 1

        # Mettre à jour le compteur de données d'apprentissage
        metrics.donnees_apprentissage_generees = donnees_generees
        metrics.save()

        # Afficher les résultats
        action = "Créées" if created else "Mises à jour"
        self.stdout.write(
            self.style.SUCCESS(f'{action} les métriques pour {target_date}:')
        )
        self.stdout.write(f'  - Total prescriptions: {total_prescriptions}')
        self.stdout.write(f'  - Taux validation directe: {taux_validation:.1f}%')
        self.stdout.write(f'  - Taux modification: {taux_modification:.1f}%')
        self.stdout.write(f'  - Taux rejet: {taux_rejet:.1f}%')
        self.stdout.write(f'  - Score moyen diagnostic: {scores_avg["diagnostic_avg"]:.1f}/10')
        self.stdout.write(f'  - Score moyen prescription: {scores_avg["prescription_avg"]:.1f}/10')
        
        if donnees_generees > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Créé {donnees_generees} nouveaux échantillons de données d\'apprentissage')
            )

    def create_learning_data(self, feedback):
        """
        Crée des données d'apprentissage anonymisées à partir d'un feedback
        """
        consultation = feedback.consultation
        patient = consultation.patient
        
        # Anonymiser les données du patient
        learning_data = AILearningData.objects.create(
            age_patient=timezone.now().year - patient.birth_date.year if patient.birth_date else 0,
            sexe_patient=patient.gender or 'non_specifie',
            symptomes_principaux=consultation.consultation_reason or '',
            antecedents_medicaux={
                'maladies': patient.diseases or '',
                'allergies': patient.allergies or '',
                'chirurgies': patient.surgeries or '',
                'medicaments': patient.actual_medecines or ''
            },
            signes_vitaux={
                'tension': consultation.tension,
                'temperature': consultation.temperature,
                'frequence_cardiaque': consultation.heart_rate,
                'poids': consultation.weight,
                'taille': consultation.height,
                'saturation_o2': consultation.oxygen_saturation
            },
            allergies_patient=patient.allergies or '',
            prescription_ia_originale=consultation.gemini_recommendations or {},
            prescription_finale_medecin=consultation.gemini_recommendations or {},
            modifications_apportees=feedback.modifications_effectuees or '',
            efficacite_traitement=feedback.efficacite_traitement,
            score_pertinence_diagnostic=feedback.pertinence_diagnostic,
            score_pertinence_prescription=feedback.pertinence_prescription,
            duree_guerison_jours=feedback.duree_guerison,
            satisfaction_patient=feedback.satisfaction_patient,
            feedback_source=feedback
        )
        
        return learning_data
```

---

### Templates

#### Template principal de feedback (`app/templates/donner_feedback.html`)

```html
{% extends 'base.html' %}
{% load static %}

{% block title %}Feedback IA - Prescription{% endblock %}

{% block extra_css %}
<style>
    .rating-stars {
        display: flex;
        gap: 5px;
        margin: 10px 0;
    }
    
    .star {
        font-size: 24px;
        color: #d1d5db;
        cursor: pointer;
        transition: color 0.2s;
    }
    
    .star.active {
        color: #fbbf24;
    }
    
    .star:hover {
        color: #f59e0b;
    }
    
    .feedback-section {
        background: #f8fafc;
        border-radius: 8px;
        padding: 20px;
        margin: 16px 0;
        border-left: 4px solid #3b82f6;
    }
    
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
    }
</style>
{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto p-6">
    <div class="bg-white rounded-lg shadow-lg p-6">
        <!-- En-tête -->
        <div class="border-b pb-4 mb-6">
            <h1 class="text-2xl font-bold text-gray-800 mb-2">
                🤖 Feedback sur la Prescription IA
            </h1>
            <div class="text-sm text-gray-600">
                <p><strong>Patient:</strong> {{ patient.first_name }} {{ patient.last_name }}</p>
                <p><strong>Consultation:</strong> {{ consultation.consultation_date|date:"d/m/Y H:i" }}</p>
                <p><strong>Diagnostic:</strong> {{ consultation.initial_diagnosis }}</p>
            </div>
        </div>

        <form method="post" class="space-y-6">
            {% csrf_token %}
            
            <!-- Section 1: Évaluation générale -->
            <div class="feedback-section">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">🎯 Évaluation Générale</h3>
                
                <div class="grid md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Type de feedback
                        </label>
                        <select name="feedback_type" class="w-full border border-gray-300 rounded-lg px-3 py-2">
                            {% for key, value in feedback_choices %}
                            <option value="{{ key }}" {% if feedback.feedback_type == key %}selected{% endif %}>
                                {{ value }}
                            </option>
                            {% endfor %}
                        </select>
                    </div>
                </div>
            </div>

            <!-- Section 2: Notation par étoiles -->
            <div class="feedback-section">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">⭐ Évaluation de la Qualité IA</h3>
                
                <div class="grid md:grid-cols-2 gap-6">
                    <!-- Pertinence Diagnostic -->
                    <div class="metric-card">
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Pertinence du Diagnostic (1-10)
                        </label>
                        <div class="rating-stars" data-rating="pertinence_diagnostic" data-value="{{ feedback.pertinence_diagnostic }}">
                            {% for i in "1234567890" %}
                                <span class="star" data-value="{{ forloop.counter }}">★</span>
                            {% endfor %}
                        </div>
                        <input type="hidden" name="pertinence_diagnostic" value="{{ feedback.pertinence_diagnostic }}">
                        <p class="text-xs text-gray-500 mt-1">Score actuel: <span class="score-display">{{ feedback.pertinence_diagnostic }}</span>/10</p>
                    </div>

                    <!-- Pertinence Prescription -->
                    <div class="metric-card">
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Pertinence de la Prescription (1-10)
                        </label>
                        <div class="rating-stars" data-rating="pertinence_prescription" data-value="{{ feedback.pertinence_prescription }}">
                            {% for i in "1234567890" %}
                                <span class="star" data-value="{{ forloop.counter }}">★</span>
                            {% endfor %}
                        </div>
                        <input type="hidden" name="pertinence_prescription" value="{{ feedback.pertinence_prescription }}">
                        <p class="text-xs text-gray-500 mt-1">Score actuel: <span class="score-display">{{ feedback.pertinence_prescription }}</span>/10</p>
                    </div>
                </div>
            </div>

            <!-- Section 3: Modifications -->
            <div class="feedback-section">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">✏️ Modifications Apportées</h3>
                
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Descriptions des modifications
                        </label>
                        <textarea name="modifications_effectuees" rows="3" 
                                  class="w-full border border-gray-300 rounded-lg px-3 py-2"
                                  placeholder="Décrivez les modifications apportées à la prescription IA...">{{ feedback.modifications_effectuees }}</textarea>
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Raison des modifications
                        </label>
                        <textarea name="raison_modification" rows="2" 
                                  class="w-full border border-gray-300 rounded-lg px-3 py-2"
                                  placeholder="Pourquoi ces modifications étaient-elles nécessaires ?">{{ feedback.raison_modification }}</textarea>
                    </div>
                </div>
            </div>

            <!-- Section 4: Suivi du traitement -->
            <div class="feedback-section">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">📈 Suivi du Traitement</h3>
                
                <div class="grid md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Efficacité du traitement
                        </label>
                        <select name="efficacite_traitement" class="w-full border border-gray-300 rounded-lg px-3 py-2">
                            {% for key, value in efficacite_choices %}
                            <option value="{{ key }}" {% if feedback.efficacite_traitement == key %}selected{% endif %}>
                                {{ value }}
                            </option>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Durée de guérison (jours)
                        </label>
                        <input type="number" name="duree_guerison" min="1" max="365" 
                               value="{{ feedback.duree_guerison|default:'' }}"
                               class="w-full border border-gray-300 rounded-lg px-3 py-2"
                               placeholder="Nombre de jours">
                    </div>
                </div>
                
                <div class="mt-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Effets secondaires observés
                    </label>
                    <textarea name="effets_secondaires_observes" rows="2" 
                              class="w-full border border-gray-300 rounded-lg px-3 py-2"
                              placeholder="Décrivez les effets secondaires observés, le cas échéant...">{{ feedback.effets_secondaires_observes }}</textarea>
                </div>
            </div>

            <!-- Section 5: Retour patient -->
            <div class="feedback-section">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">👤 Retour du Patient</h3>
                
                <div class="grid md:grid-cols-2 gap-4">
                    <div class="metric-card">
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Satisfaction du patient (1-10)
                        </label>
                        <div class="rating-stars" data-rating="satisfaction_patient" data-value="{{ feedback.satisfaction_patient|default:0 }}">
                            {% for i in "1234567890" %}
                                <span class="star" data-value="{{ forloop.counter }}">★</span>
                            {% endfor %}
                        </div>
                        <input type="hidden" name="satisfaction_patient" value="{{ feedback.satisfaction_patient|default:'' }}">
                        <p class="text-xs text-gray-500 mt-1">Score actuel: <span class="score-display">{{ feedback.satisfaction_patient|default:0 }}</span>/10</p>
                    </div>
                </div>
                
                <div class="mt-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Commentaires du patient
                    </label>
                    <textarea name="commentaires_patient" rows="2" 
                              class="w-full border border-gray-300 rounded-lg px-3 py-2"
                              placeholder="Retours et commentaires du patient sur le traitement...">{{ feedback.commentaires_patient }}</textarea>
                </div>
            </div>

            <!-- Section 6: Commentaires médecin -->
            <div class="feedback-section">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">👨‍⚕️ Commentaires Médecin</h3>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Observations et recommandations
                    </label>
                    <textarea name="commentaires_medecin" rows="3" 
                              class="w-full border border-gray-300 rounded-lg px-3 py-2"
                              placeholder="Vos observations sur la prescription IA, suggestions d'amélioration...">{{ feedback.commentaires_medecin }}</textarea>
                </div>
                
                <div class="mt-4">
                    <label class="flex items-center">
                        <input type="checkbox" name="suivi_complete" class="mr-2" 
                               {% if feedback.suivi_complete %}checked{% endif %}>
                        <span class="text-sm font-medium text-gray-700">
                            Marquer ce suivi comme terminé (génère des données d'apprentissage)
                        </span>
                    </label>
                </div>
            </div>

            <!-- Boutons d'action -->
            <div class="flex justify-between items-center pt-6 border-t">
                <a href="{% url 'dashboard' %}" 
                   class="bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-6 rounded-lg transition-colors">
                    ← Retour
                </a>
                
                <button type="submit" 
                        class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors">
                    💾 Enregistrer le Feedback
                </button>
            </div>
        </form>
    </div>
</div>

<!-- JavaScript pour les étoiles de notation -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser toutes les sections de notation par étoiles
    document.querySelectorAll('.rating-stars').forEach(container => {
        const stars = container.querySelectorAll('.star');
        const ratingName = container.dataset.rating;
        const hiddenInput = document.querySelector(`input[name="${ratingName}"]`);
        const scoreDisplay = container.nextElementSibling.nextElementSibling.querySelector('.score-display');
        const currentValue = parseInt(container.dataset.value) || 0;
        
        // Initialiser l'affichage des étoiles
        updateStars(stars, currentValue);
        
        stars.forEach((star, index) => {
            star.addEventListener('click', () => {
                const value = index + 1;
                hiddenInput.value = value;
                scoreDisplay.textContent = value;
                updateStars(stars, value);
            });
            
            star.addEventListener('mouseenter', () => {
                const value = index + 1;
                updateStars(stars, value);
            });
        });
        
        container.addEventListener('mouseleave', () => {
            const currentValue = parseInt(hiddenInput.value) || 0;
            updateStars(stars, currentValue);
        });
    });
    
    function updateStars(stars, value) {
        stars.forEach((star, index) => {
            if (index < value) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }
});
</script>
{% endblock %}
```

---

## 🎯 Points Clés Techniques

### 1. **Relations de Base de Données**
- `OneToOneField` entre `Consultation` et `PrescriptionFeedback`
- `ForeignKey` pour lier feedback aux médecins
- Contraintes de validation sur les scores (1-10)

### 2. **Calcul Automatique des Métriques**
- Agrégations Django pour les moyennes et comptages
- Calculs de pourcentages avec arrondi à 2 décimales
- Génération automatique de données d'apprentissage

### 3. **Interface d'Administration Avancée**
- Vues personnalisées avec `get_urls()`
- Intégration Chart.js pour les graphiques
- Fieldsets organisés par catégorie logique

### 4. **Templates Responsives**
- Grid CSS avec Tailwind pour l'adaptabilité
- JavaScript vanilla pour l'interactivité
- Système de notation par étoiles intuitif

### 5. **Sécurité et Validation**
- Protection CSRF sur tous les formulaires
- Validation des entrées utilisateur
- Gestion des erreurs avec try/catch

Cette architecture garantit une solution robuste, évolutive et facile à maintenir pour l'amélioration continue de l'IA médicale.
