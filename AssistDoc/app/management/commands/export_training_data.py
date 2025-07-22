from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import json
import os
from app.models import AILearningData, PrescriptionFeedback


class Command(BaseCommand):
    help = 'Exporte les données d\'apprentissage pour fine-tuning Gemini'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            choices=['gemini', 'openai', 'generic'],
            default='gemini',
            help='Format d\'export (défaut: gemini)',
        )
        parser.add_argument(
            '--period',
            type=str,
            choices=['weekly', 'monthly', 'all'],
            default='monthly',
            help='Période de données à exporter (défaut: monthly)',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='training_data.jsonl',
            help='Fichier de sortie (défaut: training_data.jsonl)',
        )
        parser.add_argument(
            '--min-score',
            type=int,
            default=7,
            help='Score minimum de pertinence pour inclure les données (défaut: 7)',
        )

    def handle(self, *args, **options):
        export_format = options['format']
        period = options['period']
        output_file = options['output']
        min_score = options['min_score']
        
        self.stdout.write(f'🚀 Export des données pour fine-tuning ({export_format})...')
        
        # Déterminer la période
        if period == 'weekly':
            start_date = timezone.now() - timedelta(weeks=1)
        elif period == 'monthly':
            start_date = timezone.now() - timedelta(days=30)
        else:  # all
            start_date = None
        
        # Récupérer les données d'apprentissage
        query = AILearningData.objects.filter(
            score_pertinence_diagnostic__gte=min_score,
            score_pertinence_prescription__gte=min_score,
            utilise_pour_entrainement=False  # Pas encore utilisées
        )
        
        if start_date:
            query = query.filter(date_creation__gte=start_date)
        
        learning_data = query.order_by('-date_creation')
        
        if not learning_data.exists():
            self.stdout.write(
                self.style.WARNING('Aucune donnée d\'apprentissage trouvée avec les critères spécifiés.')
            )
            return
        
        self.stdout.write(f'📊 {learning_data.count()} échantillons trouvés.')
        
        # Exporter selon le format
        if export_format == 'gemini':
            exported_count = self.export_gemini_format(learning_data, output_file)
        elif export_format == 'openai':
            exported_count = self.export_openai_format(learning_data, output_file)
        else:
            exported_count = self.export_generic_format(learning_data, output_file)
        
        # Marquer les données comme utilisées
        learning_data.update(utilise_pour_entrainement=True, cycle_entrainement=f'{export_format}_{timezone.now().strftime("%Y%m%d")}')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Export terminé: {exported_count} échantillons exportés vers {output_file}')
        )

    def export_gemini_format(self, learning_data, output_file):
        """Export au format JSONL pour Google AI Studio"""
        exported_count = 0
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for data in learning_data:
                # Construire l'échantillon d'entraînement
                training_sample = {
                    "messages": [
                        {
                            "role": "user",
                            "content": self.build_user_prompt(data)
                        },
                        {
                            "role": "assistant", 
                            "content": json.dumps(data.prescription_finale_medecin, ensure_ascii=False)
                        }
                    ]
                }
                
                f.write(json.dumps(training_sample, ensure_ascii=False) + '\n')
                exported_count += 1
        
        return exported_count

    def export_openai_format(self, learning_data, output_file):
        """Export au format OpenAI fine-tuning"""
        exported_count = 0
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for data in learning_data:
                training_sample = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "Tu es un médecin expert. Analyse les données patient et fournis des recommandations médicales optimales."
                        },
                        {
                            "role": "user",
                            "content": self.build_user_prompt(data)
                        },
                        {
                            "role": "assistant",
                            "content": json.dumps(data.prescription_finale_medecin, ensure_ascii=False)
                        }
                    ]
                }
                
                f.write(json.dumps(training_sample, ensure_ascii=False) + '\n')
                exported_count += 1
        
        return exported_count

    def export_generic_format(self, learning_data, output_file):
        """Export au format générique JSON"""
        training_samples = []
        
        for data in learning_data:
            sample = {
                "id": str(data.id),
                "patient_data": {
                    "age": data.age_patient,
                    "sexe": data.sexe_patient,
                    "symptomes": data.symptomes_principaux,
                    "antecedents": data.antecedents_medicaux,
                    "signes_vitaux": data.signes_vitaux,
                    "allergies": data.allergies_patient
                },
                "ai_prescription": data.prescription_ia_originale,
                "doctor_prescription": data.prescription_finale_medecin,
                "modifications": data.modifications_apportees,
                "efficacy": data.efficacite_traitement,
                "scores": {
                    "diagnostic": data.score_pertinence_diagnostic,
                    "prescription": data.score_pertinence_prescription
                },
                "satisfaction": data.satisfaction_patient,
                "created_at": data.date_creation.isoformat()
            }
            training_samples.append(sample)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(training_samples, f, ensure_ascii=False, indent=2)
        
        return len(training_samples)

    def build_user_prompt(self, data):
        """Construit le prompt utilisateur à partir des données"""
        prompt = f"""Analyse ce patient et fournis tes recommandations:

PATIENT:
- Âge: {data.age_patient} ans
- Sexe: {data.sexe_patient}
- Symptômes: {data.symptomes_principaux}
- Allergies: {data.allergies_patient or "Aucune"}

ANTÉCÉDENTS:
{json.dumps(data.antecedents_medicaux, ensure_ascii=False, indent=2)}

SIGNES VITAUX:
{json.dumps(data.signes_vitaux, ensure_ascii=False, indent=2)}

Fournis un diagnostic et des prescriptions détaillées au format JSON."""
        
        return prompt
