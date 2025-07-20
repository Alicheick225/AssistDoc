from django.core.management.base import BaseCommand
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
from app.models import PrescriptionFeedback, IAPerformanceMetrics, AILearningData

class Command(BaseCommand):
    help = 'Calcule et met à jour les métriques de performance de l\'IA'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date pour laquelle calculer les métriques (format YYYY-MM-DD). Par défaut: aujourd\'hui'
        )

    def handle(self, *args, **options):
        # Déterminer la date
        if options['date']:
            try:
                date_calcul = datetime.strptime(options['date'], '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(self.style.ERROR('Format de date invalide. Utilisez YYYY-MM-DD'))
                return
        else:
            date_calcul = datetime.now().date()

        self.stdout.write(f'Calcul des métriques pour le {date_calcul}...')

        # Récupérer les feedbacks jusqu'à cette date
        feedbacks = PrescriptionFeedback.objects.filter(
            date_creation__date__lte=date_calcul
        )

        if not feedbacks.exists():
            self.stdout.write(self.style.WARNING('Aucun feedback trouvé pour cette période'))
            return

        # Calculer les métriques
        total_prescriptions = feedbacks.count()
        
        # Compter par type de feedback
        validees_directement = feedbacks.filter(feedback_type='validee_directement').count()
        modifiees = feedbacks.filter(feedback_type='modifiee').count()
        rejetees = feedbacks.filter(feedback_type='annulee').count()

        # Calculer les taux (en pourcentage)
        taux_validation_directe = (validees_directement / total_prescriptions) * 100 if total_prescriptions > 0 else 0
        taux_modification = (modifiees / total_prescriptions) * 100 if total_prescriptions > 0 else 0
        taux_rejet = (rejetees / total_prescriptions) * 100 if total_prescriptions > 0 else 0

        # Calculer les scores moyens
        scores = feedbacks.aggregate(
            score_moyen_diagnostic=Avg('pertinence_diagnostic'),
            score_moyen_prescription=Avg('pertinence_prescription'),
            satisfaction_moyenne_patients=Avg('satisfaction_patient')
        )

        # Métriques d'efficacité
        feedbacks_avec_suivi = feedbacks.exclude(efficacite_traitement='non_evalue')
        efficaces = feedbacks_avec_suivi.filter(
            efficacite_traitement__in=['tres_efficace', 'efficace']
        )
        taux_efficacite_elevee = (efficaces.count() / feedbacks_avec_suivi.count()) * 100 if feedbacks_avec_suivi.count() > 0 else 0

        # Durée moyenne de guérison
        duree_moyenne_guerison = feedbacks_avec_suivi.filter(
            duree_guerison__isnull=False
        ).aggregate(avg_duree=Avg('duree_guerison'))['avg_duree']

        # Créer ou mettre à jour les métriques
        metrics, created = IAPerformanceMetrics.objects.get_or_create(
            date_calcul=date_calcul,
            defaults={
                'total_prescriptions': total_prescriptions,
                'prescriptions_validees_directement': validees_directement,
                'prescriptions_modifiees': modifiees,
                'prescriptions_rejetees': rejetees,
                'taux_validation_directe': round(taux_validation_directe, 2),
                'taux_modification': round(taux_modification, 2),
                'taux_rejet': round(taux_rejet, 2),
                'score_moyen_diagnostic': round(scores['score_moyen_diagnostic'] or 0, 1),
                'score_moyen_prescription': round(scores['score_moyen_prescription'] or 0, 1),
                'taux_efficacite_elevee': round(taux_efficacite_elevee, 2),
                'duree_moyenne_guerison': round(duree_moyenne_guerison, 1) if duree_moyenne_guerison else None,
                'satisfaction_moyenne_patients': round(scores['satisfaction_moyenne_patients'] or 0, 1),
                'satisfaction_moyenne_medecins': round((scores['score_moyen_diagnostic'] or 0 + scores['score_moyen_prescription'] or 0) / 2, 1)
            }
        )

        if not created:
            # Mettre à jour si existe déjà
            metrics.total_prescriptions = total_prescriptions
            metrics.prescriptions_validees_directement = validees_directement
            metrics.prescriptions_modifiees = modifiees
            metrics.prescriptions_rejetees = rejetees
            metrics.taux_validation_directe = round(taux_validation_directe, 2)
            metrics.taux_modification = round(taux_modification, 2)
            metrics.taux_rejet = round(taux_rejet, 2)
            metrics.score_moyen_diagnostic = round(scores['score_moyen_diagnostic'] or 0, 1)
            metrics.score_moyen_prescription = round(scores['score_moyen_prescription'] or 0, 1)
            metrics.taux_efficacite_elevee = round(taux_efficacite_elevee, 2)
            metrics.duree_moyenne_guerison = round(duree_moyenne_guerison, 1) if duree_moyenne_guerison else None
            metrics.satisfaction_moyenne_patients = round(scores['satisfaction_moyenne_patients'] or 0, 1)
            metrics.satisfaction_moyenne_medecins = round((scores['score_moyen_diagnostic'] or 0 + scores['score_moyen_prescription'] or 0) / 2, 1)
            metrics.save()

        # Générer des données d'apprentissage pour les nouveaux feedbacks
        self.generate_learning_data(date_calcul)

        action = "Créées" if created else "Mises à jour"
        self.stdout.write(
            self.style.SUCCESS(
                f'{action} les métriques pour {date_calcul}:\n'
                f'  - Total prescriptions: {total_prescriptions}\n'
                f'  - Taux validation directe: {taux_validation_directe:.1f}%\n'
                f'  - Taux modification: {taux_modification:.1f}%\n'
                f'  - Score moyen diagnostic: {scores["score_moyen_diagnostic"] or 0:.1f}/10\n'
                f'  - Score moyen prescription: {scores["score_moyen_prescription"] or 0:.1f}/10'
            )
        )

    def generate_learning_data(self, date_calcul):
        """Génère des données d'apprentissage à partir des feedbacks validés"""
        
        # Récupérer les feedbacks avec suivi complet qui n'ont pas encore de données d'apprentissage
        feedbacks_completés = PrescriptionFeedback.objects.filter(
            date_creation__date=date_calcul,
            suivi_complete=True
        ).exclude(
            id__in=AILearningData.objects.values_list('feedback_source_id', flat=True)
        )

        learning_data_created = 0
        
        for feedback in feedbacks_completés:
            consultation = feedback.consultation
            patient = consultation.patient
            
            # Préparer les données anonymisées
            try:
                learning_data = AILearningData.objects.create(
                    age_patient=datetime.now().year - patient.birth_date.year if patient.birth_date else 0,
                    sexe_patient=patient.gender or 'Non spécifié',
                    symptomes_principaux=consultation.consultation_reason,
                    antecedents_medicaux=f"Maladies: {patient.diseases or 'Aucune'}, Allergies: {patient.allergies or 'Aucune'}",
                    signes_vitaux={
                        'tension': float(consultation.tension) if consultation.tension else None,
                        'temperature': float(consultation.temperature) if consultation.temperature else None,
                        'frequence_cardiaque': consultation.heart_rate,
                        'poids': float(consultation.weight) if consultation.weight else None,
                        'taille': float(consultation.height) if consultation.height else None,
                        'saturation_oxygene': float(consultation.oxygen_saturation) if consultation.oxygen_saturation else None
                    },
                    prescription_ia_originale=consultation.gemini_recommendations or {},
                    diagnostic_ia_original=consultation.initial_diagnosis,
                    prescription_finale_medecin=consultation.gemini_recommendations or {},  # Sera mis à jour avec les modifications
                    diagnostic_final_medecin=consultation.initial_diagnosis,
                    efficacite_traitement=feedback.efficacite_traitement,
                    effets_secondaires=feedback.effets_secondaires_observes or '',
                    duree_guerison=feedback.duree_guerison,
                    score_pertinence_diagnostic=feedback.pertinence_diagnostic,
                    score_pertinence_prescription=feedback.pertinence_prescription,
                    feedback_source=feedback
                )
                learning_data_created += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Erreur lors de la création des données d\'apprentissage pour le feedback {feedback.id}: {e}')
                )

        if learning_data_created > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Créé {learning_data_created} nouveaux échantillons de données d\'apprentissage')
            )
