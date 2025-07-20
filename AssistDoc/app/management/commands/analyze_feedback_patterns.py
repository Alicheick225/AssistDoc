from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from app.models import PrescriptionFeedback, FeedbackPattern
import re
from collections import Counter


class Command(BaseCommand):
    help = 'Analyse les patterns de feedback pour améliorer les prompts Gemini'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Nombre de jours à analyser (défaut: 7)',
        )

    def handle(self, *args, **options):
        days = options['days']
        start_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f'Analyse des patterns de feedback des {days} derniers jours...')
        
        # Récupérer les feedbacks récents
        recent_feedbacks = PrescriptionFeedback.objects.filter(
            date_creation__gte=start_date
        )
        
        if not recent_feedbacks.exists():
            self.stdout.write(
                self.style.WARNING(f'Aucun feedback trouvé pour les {days} derniers jours')
            )
            return
        
        # Analyser les patterns
        self.analyze_modification_patterns(recent_feedbacks)
        self.analyze_rejection_patterns(recent_feedbacks)
        self.analyze_good_practices(recent_feedbacks)
        self.analyze_dosage_patterns(recent_feedbacks)
        
        self.stdout.write(
            self.style.SUCCESS('Analyse des patterns terminée avec succès!')
        )

    def analyze_modification_patterns(self, feedbacks):
        """Analyse les raisons de modifications fréquentes"""
        modified_feedbacks = feedbacks.filter(feedback_type='modifiee')
        
        if not modified_feedbacks.exists():
            return
        
        # Extraire les raisons de modification
        modification_reasons = []
        for feedback in modified_feedbacks:
            if feedback.raison_modification:
                modification_reasons.append(feedback.raison_modification.lower())
        
        if not modification_reasons:
            return
        
        # Analyser les mots-clés fréquents
        common_keywords = self.extract_common_keywords(modification_reasons)
        
        for keyword, frequency in common_keywords.most_common(5):
            if frequency >= 2:  # Au moins 2 occurrences
                FeedbackPattern.objects.update_or_create(
                    pattern_type='frequent_modification',
                    description=f'Modification fréquente liée à: {keyword}',
                    defaults={
                        'frequency': frequency,
                        'confidence_score': min(frequency / len(modification_reasons), 1.0)
                    }
                )
        
        self.stdout.write(f'  - Analysé {len(modification_reasons)} raisons de modification')

    def analyze_rejection_patterns(self, feedbacks):
        """Analyse les patterns de rejets/annulations"""
        rejected_feedbacks = feedbacks.filter(feedback_type='annulee')
        
        if not rejected_feedbacks.exists():
            return
        
        # Analyser les commentaires de rejet
        rejection_comments = []
        for feedback in rejected_feedbacks:
            if feedback.commentaires_medecin:
                rejection_comments.append(feedback.commentaires_medecin.lower())
        
        if rejection_comments:
            common_issues = self.extract_common_keywords(rejection_comments)
            
            for issue, frequency in common_issues.most_common(3):
                if frequency >= 2:
                    FeedbackPattern.objects.update_or_create(
                        pattern_type='frequent_rejection',
                        description=f'Erreur fréquente causant rejet: {issue}',
                        defaults={
                            'frequency': frequency,
                            'confidence_score': min(frequency / len(rejection_comments), 1.0)
                        }
                    )
        
        self.stdout.write(f'  - Analysé {len(rejection_comments)} raisons de rejet')

    def analyze_good_practices(self, feedbacks):
        """Analyse les bonnes pratiques (feedbacks positifs)"""
        good_feedbacks = feedbacks.filter(
            feedback_type='validee_directement',
            pertinence_diagnostic__gte=8,
            pertinence_prescription__gte=8
        )
        
        if not good_feedbacks.exists():
            return
        
        # Analyser les diagnostics bien notés
        successful_diagnoses = []
        for feedback in good_feedbacks:
            if feedback.consultation.initial_diagnosis:
                successful_diagnoses.append(feedback.consultation.initial_diagnosis.lower())
        
        if successful_diagnoses:
            successful_patterns = self.extract_common_keywords(successful_diagnoses)
            
            for pattern, frequency in successful_patterns.most_common(3):
                if frequency >= 2:
                    FeedbackPattern.objects.update_or_create(
                        pattern_type='good_practice',
                        description=f'Diagnostic bien validé: {pattern}',
                        defaults={
                            'frequency': frequency,
                            'confidence_score': min(frequency / len(successful_diagnoses), 1.0)
                        }
                    )
        
        self.stdout.write(f'  - Analysé {good_feedbacks.count()} bonnes pratiques')

    def analyze_dosage_patterns(self, feedbacks):
        """Analyse les patterns de dosage préférés par les médecins"""
        modified_prescriptions = feedbacks.filter(
            feedback_type='modifiee',
            modifications_effectuees__isnull=False
        )
        
        dosage_modifications = []
        for feedback in modified_prescriptions:
            modifications = feedback.modifications_effectuees.lower()
            
            # Rechercher les mentions de dosage
            dosage_patterns = re.findall(r'(\d+)\s*(mg|g|ml|comprimé|gélule)', modifications)
            for dosage, unit in dosage_patterns:
                dosage_modifications.append(f'{dosage}{unit}')
        
        if dosage_modifications:
            common_dosages = Counter(dosage_modifications)
            
            for dosage, frequency in common_dosages.most_common(5):
                if frequency >= 2:
                    FeedbackPattern.objects.update_or_create(
                        pattern_type='dosage_preference',
                        description=f'Dosage préféré par médecins: {dosage}',
                        defaults={
                            'frequency': frequency,
                            'confidence_score': min(frequency / len(dosage_modifications), 1.0)
                        }
                    )
        
        self.stdout.write(f'  - Analysé {len(dosage_modifications)} modifications de dosage')

    def extract_common_keywords(self, texts):
        """Extrait les mots-clés communs des textes"""
        # Mots à ignorer
        stop_words = {
            'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'ou', 'mais',
            'pour', 'par', 'avec', 'sans', 'sur', 'dans', 'à', 'au', 'aux',
            'prescription', 'médicament', 'traitement', 'patient', 'médecin'
        }
        
        # Extraire tous les mots
        all_words = []
        for text in texts:
            # Nettoyer et diviser le texte
            words = re.findall(r'\b[a-záàâäéèêëíìîïóòôöúùûüýÿç]+\b', text.lower())
            # Filtrer les mots courts et les stop words
            words = [word for word in words if len(word) > 3 and word not in stop_words]
            all_words.extend(words)
        
        return Counter(all_words)
