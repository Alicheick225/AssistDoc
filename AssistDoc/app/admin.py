from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Avg, Q
from django.utils.html import format_html
import json
from datetime import datetime, timedelta
from .models import (
    User, Hospital, Patient, Consultation, 
    PrescriptionFeedback, AILearningData, IAPerformanceMetrics, FeedbackPattern
)

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

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'consultation_date', 'is_validated', 'has_feedback')
    list_filter = ('is_validated', 'consultation_date', 'doctor')
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__username')
    date_hierarchy = 'consultation_date'
    
    def has_feedback(self, obj):
        return hasattr(obj, 'feedback')
    has_feedback.boolean = True
    has_feedback.short_description = 'Feedback donné'

@admin.register(PrescriptionFeedback)
class PrescriptionFeedbackAdmin(admin.ModelAdmin):
    list_display = ('consultation_patient', 'doctor', 'feedback_type', 'efficacite_traitement', 
                   'pertinence_diagnostic', 'pertinence_prescription', 'date_creation', 'suivi_complete')
    list_filter = ('feedback_type', 'efficacite_traitement', 'suivi_complete', 'date_creation')
    search_fields = ('consultation__patient__first_name', 'consultation__patient__last_name', 'doctor__username')
    date_hierarchy = 'date_creation'
    readonly_fields = ('date_creation', 'date_mise_a_jour')
    
    fieldsets = (
        ('Information de base', {
            'fields': ('consultation', 'doctor', 'feedback_type')
        }),
        ('Modifications (si applicable)', {
            'fields': ('modifications_effectuees', 'raison_modification'),
            'classes': ('collapse',)
        }),
        ('Évaluation du traitement', {
            'fields': ('efficacite_traitement', 'effets_secondaires_observes', 'duree_guerison', 'suivi_complete')
        }),
        ('Retour patient', {
            'fields': ('satisfaction_patient', 'commentaires_patient'),
            'classes': ('collapse',)
        }),
        ('Évaluation IA', {
            'fields': ('pertinence_diagnostic', 'pertinence_prescription', 'commentaires_medecin')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_mise_a_jour'),
            'classes': ('collapse',)
        })
    )
    
    def consultation_patient(self, obj):
        return f"{obj.consultation.patient.get_full_name()} - {obj.consultation.consultation_date.strftime('%d/%m/%Y')}"
    consultation_patient.short_description = 'Patient / Date'

@admin.register(AILearningData)
class AILearningDataAdmin(admin.ModelAdmin):
    list_display = ('patient_info', 'efficacite_traitement', 'score_pertinence_diagnostic', 
                   'score_pertinence_prescription', 'date_creation', 'utilise_pour_entrainement')
    list_filter = ('efficacite_traitement', 'utilise_pour_entrainement', 'sexe_patient', 'date_creation')
    search_fields = ('symptomes_principaux', 'diagnostic_final_medecin')
    date_hierarchy = 'date_creation'
    readonly_fields = ('date_creation',)
    
    def patient_info(self, obj):
        return f"{obj.sexe_patient}, {obj.age_patient} ans"
    patient_info.short_description = 'Info Patient'

class IAPerformanceMetricsAdmin(admin.ModelAdmin):
    list_display = ('date_calcul', 'total_prescriptions', 'taux_validation_directe', 
                   'taux_modification', 'score_moyen_diagnostic', 'score_moyen_prescription')
    list_filter = ('date_calcul',)
    date_hierarchy = 'date_calcul'
    readonly_fields = ('date_calcul', 'total_prescriptions', 'prescriptions_validees_directement',
                      'prescriptions_modifiees', 'prescriptions_rejetees', 'taux_validation_directe',
                      'taux_modification', 'taux_rejet', 'score_moyen_diagnostic', 'score_moyen_prescription')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_site.admin_view(self.analytics_view), name='app_iaperformancemetrics_analytics'),
        ]
        return custom_urls + urls
    
    def analytics_view(self, request):
        """Vue personnalisée pour afficher les graphiques et analyses"""
        
        # Données pour les graphiques
        context = {
            'title': 'Analytics IA - AssistDoc',
            'subtitle': 'Analyse de performance et apprentissage automatique',
        }
        
        # Métriques de performance des 30 derniers jours
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        metrics = IAPerformanceMetrics.objects.filter(
            date_calcul__range=[start_date, end_date]
        ).order_by('date_calcul')
        
        # Préparer les données pour les graphiques
        dates = [m.date_calcul.strftime('%Y-%m-%d') for m in metrics]
        taux_validation = [float(m.taux_validation_directe) for m in metrics]
        taux_modification = [float(m.taux_modification) for m in metrics]
        scores_diagnostic = [float(m.score_moyen_diagnostic) for m in metrics]
        scores_prescription = [float(m.score_moyen_prescription) for m in metrics]
        
        context.update({
            'dates_json': json.dumps(dates),
            'taux_validation_json': json.dumps(taux_validation),
            'taux_modification_json': json.dumps(taux_modification),
            'scores_diagnostic_json': json.dumps(scores_diagnostic),
            'scores_prescription_json': json.dumps(scores_prescription),
        })
        
        # Statistiques globales
        total_feedbacks = PrescriptionFeedback.objects.count()
        feedbacks_aujourd_hui = PrescriptionFeedback.objects.filter(
            date_creation__date=datetime.now().date()
        ).count()
        
        # Répartition des types de feedback
        feedback_stats = PrescriptionFeedback.objects.values('feedback_type').annotate(
            count=Count('id')
        )
        
        feedback_labels = []
        feedback_counts = []
        for stat in feedback_stats:
            feedback_labels.append(dict(PrescriptionFeedback.FEEDBACK_CHOICES)[stat['feedback_type']])
            feedback_counts.append(stat['count'])
        
        # Efficacité des traitements
        efficacite_stats = PrescriptionFeedback.objects.exclude(
            efficacite_traitement='non_evalue'
        ).values('efficacite_traitement').annotate(count=Count('id'))
        
        efficacite_labels = []
        efficacite_counts = []
        for stat in efficacite_stats:
            efficacite_labels.append(dict(PrescriptionFeedback.EFFICACITE_CHOICES)[stat['efficacite_traitement']])
            efficacite_counts.append(stat['count'])
        
        # Moyennes des scores
        avg_scores = PrescriptionFeedback.objects.aggregate(
            avg_diagnostic=Avg('pertinence_diagnostic'),
            avg_prescription=Avg('pertinence_prescription'),
            avg_satisfaction=Avg('satisfaction_patient')
        )
        
        context.update({
            'total_feedbacks': total_feedbacks,
            'feedbacks_aujourd_hui': feedbacks_aujourd_hui,
            'feedback_labels_json': json.dumps(feedback_labels),
            'feedback_counts_json': json.dumps(feedback_counts),
            'efficacite_labels_json': json.dumps(efficacite_labels),
            'efficacite_counts_json': json.dumps(efficacite_counts),
            'avg_diagnostic': round(avg_scores['avg_diagnostic'] or 0, 1),
            'avg_prescription': round(avg_scores['avg_prescription'] or 0, 1),
            'avg_satisfaction': round(avg_scores['avg_satisfaction'] or 0, 1),
        })
        
        # Données d'apprentissage
        learning_data_count = AILearningData.objects.count()
        learning_data_used = AILearningData.objects.filter(utilise_pour_entrainement=True).count()
        
        context.update({
            'learning_data_count': learning_data_count,
            'learning_data_used': learning_data_used,
            'learning_data_pending': learning_data_count - learning_data_used,
        })
        
        return render(request, 'admin/app/iaperformancemetrics/analytics.html', context)

# Enregistrer le modèle avec la classe admin personnalisée
admin.site.register(IAPerformanceMetrics, IAPerformanceMetricsAdmin)

@admin.register(FeedbackPattern)
class FeedbackPatternAdmin(admin.ModelAdmin):
    list_display = ('pattern_type', 'description_short', 'frequency', 'confidence_score', 
                   'reliability_level', 'is_active', 'last_occurrence')
    list_filter = ('pattern_type', 'is_active', 'last_occurrence')
    search_fields = ('description',)
    date_hierarchy = 'last_occurrence'
    readonly_fields = ('first_occurrence', 'last_occurrence', 'reliability_level')
    
    fieldsets = (
        ('Information Générale', {
            'fields': ('pattern_type', 'description', 'is_active')
        }),
        ('Statistiques', {
            'fields': ('frequency', 'confidence_score', 'reliability_level'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('first_occurrence', 'last_occurrence'),
            'classes': ('collapse',)
        }),
        ('Relations', {
            'fields': ('related_feedbacks',),
            'classes': ('collapse',)
        }),
    )
    
    def description_short(self, obj):
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'
    
    actions = ['activate_patterns', 'deactivate_patterns', 'refresh_confidence_scores']
    
    def activate_patterns(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} patterns activés avec succès.')
    activate_patterns.short_description = "Activer les patterns sélectionnés"
    
    def deactivate_patterns(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} patterns désactivés avec succès.')
    deactivate_patterns.short_description = "Désactiver les patterns sélectionnés"
    
    def refresh_confidence_scores(self, request, queryset):
        from .prompt_enhancement import refresh_prompt_patterns
        result = refresh_prompt_patterns()
        self.message_user(request, 
            f'Scores actualisés: {result["active_patterns"]} patterns actifs, '
            f'{result["deactivated_patterns"]} patterns désactivés.')
    refresh_confidence_scores.short_description = "Actualiser les scores de confiance"

# Personnalisation du site admin
admin.site.site_header = "AssistDoc - Administration IA"
admin.site.site_title = "AssistDoc Admin"
admin.site.index_title = "Gestion du système d'assistance médicale"
