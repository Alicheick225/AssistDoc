from django.core.management.base import BaseCommand
from django.core.management import call_command
from app.prompt_enhancement import refresh_prompt_patterns


class Command(BaseCommand):
    help = 'Tâche quotidienne: analyse patterns + calcul métriques + nettoyage système'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Début de la tâche quotidienne d\'amélioration IA...')
        )
        
        try:
            # 1. Analyser les nouveaux patterns de feedback
            self.stdout.write('📊 Analyse des patterns de feedback...')
            call_command('analyze_feedback_patterns', '--days', 7)
            
            # 2. Calculer les métriques de performance
            self.stdout.write('📈 Calcul des métriques de performance...')
            call_command('calculate_ai_metrics')
            
            # 3. Actualiser les patterns de prompt
            self.stdout.write('🔄 Actualisation des patterns de prompt...')
            result = refresh_prompt_patterns()
            
            self.stdout.write(
                f'  - Patterns actifs: {result["active_patterns"]}'
            )
            self.stdout.write(
                f'  - Patterns désactivés: {result["deactivated_patterns"]}'
            )
            
            # 4. Résumé final
            self.stdout.write(
                self.style.SUCCESS('✅ Tâche quotidienne terminée avec succès!')
            )
            
            # Afficher un résumé
            from app.prompt_enhancement import get_prompt_enhancement_summary
            summary = get_prompt_enhancement_summary()
            
            if summary:
                self.stdout.write('\n📋 Résumé des améliorations disponibles:')
                for pattern_name, data in summary.items():
                    self.stdout.write(f'  - {pattern_name}: {data["count"]} patterns')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de la tâche quotidienne: {str(e)}')
            )
            raise e
