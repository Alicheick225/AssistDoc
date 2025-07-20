"""
Utilitaires pour l'enrichissement automatique des prompts Gemini
basé sur l'analyse des feedbacks médecins
"""
from django.utils import timezone
from datetime import timedelta
from app.models import FeedbackPattern, PrescriptionFeedback
from django.db.models import Avg, Count


def get_enhanced_system_instruction(base_instruction):
    """
    Enrichit le prompt système de base avec les patterns de feedback récents
    
    Args:
        base_instruction (str): Instruction système de base pour Gemini
        
    Returns:
        str: Instruction système enrichie avec les patterns de feedback
    """
    
    # Récupérer les patterns actifs et fiables
    active_patterns = FeedbackPattern.objects.filter(
        is_active=True,
        frequency__gte=2,  # Au moins 2 occurrences
        confidence_score__gte=0.3  # Score de confiance minimum
    ).order_by('-frequency', '-confidence_score')
    
    if not active_patterns.exists():
        return base_instruction
    
    # Construire l'enrichissement
    enhancement_sections = []
    
    # 1. Erreurs fréquentes à éviter
    frequent_errors = active_patterns.filter(
        pattern_type__in=['frequent_modification', 'frequent_rejection', 'diagnostic_error', 'prescription_error']
    )[:5]
    
    if frequent_errors.exists():
        error_section = "\n🚨 ERREURS FRÉQUENTES À ÉVITER (basé sur feedback médecins):\n"
        for pattern in frequent_errors:
            reliability = pattern.reliability_level
            error_section += f"- {pattern.description} (fiabilité: {reliability})\n"
        enhancement_sections.append(error_section)
    
    # 2. Bonnes pratiques validées
    good_practices = active_patterns.filter(pattern_type='good_practice')[:3]
    
    if good_practices.exists():
        practice_section = "\n✅ BONNES PRATIQUES VALIDÉES (feedback positifs médecins):\n"
        for pattern in good_practices:
            practice_section += f"- {pattern.description}\n"
        enhancement_sections.append(practice_section)
    
    # 3. Préférences de dosage
    dosage_preferences = active_patterns.filter(pattern_type='dosage_preference')[:3]
    
    if dosage_preferences.exists():
        dosage_section = "\n💊 DOSAGES PRÉFÉRÉS PAR LES MÉDECINS:\n"
        for pattern in dosage_preferences:
            dosage_section += f"- {pattern.description}\n"
        enhancement_sections.append(dosage_section)
    
    # 4. Statistiques récentes de performance
    performance_stats = get_recent_performance_stats()
    if performance_stats:
        stats_section = f"\n📊 PERFORMANCE IA RÉCENTE:\n{performance_stats}\n"
        enhancement_sections.append(stats_section)
    
    # Assembler l'instruction enrichie
    if enhancement_sections:
        enhanced_instruction = base_instruction + "\n\n" + "".join(enhancement_sections)
        enhanced_instruction += "\n⚠️ IMPORTANT: Utilise ces informations pour améliorer tes recommandations, mais garde toujours ton jugement médical principal.\n"
        return enhanced_instruction
    
    return base_instruction


def get_recent_performance_stats():
    """
    Récupère les statistiques de performance récentes pour informer l'IA
    
    Returns:
        str: Statistiques formatées pour le prompt
    """
    # Feedbacks des 7 derniers jours
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_feedbacks = PrescriptionFeedback.objects.filter(
        date_creation__gte=seven_days_ago
    )
    
    if not recent_feedbacks.exists():
        return None
    
    # Calculer les statistiques
    total_count = recent_feedbacks.count()
    validation_rate = recent_feedbacks.filter(feedback_type='validee_directement').count() / total_count * 100
    avg_diagnostic_score = recent_feedbacks.aggregate(avg=Avg('pertinence_diagnostic'))['avg'] or 0
    avg_prescription_score = recent_feedbacks.aggregate(avg=Avg('pertinence_prescription'))['avg'] or 0
    
    stats = f"""- Taux de validation directe cette semaine: {validation_rate:.1f}%
- Score moyen diagnostic: {avg_diagnostic_score:.1f}/10
- Score moyen prescription: {avg_prescription_score:.1f}/10
- Total feedbacks analysés: {total_count}"""
    
    return stats


def get_contextual_enhancements(symptoms=None, patient_age=None, patient_gender=None):
    """
    Récupère des enrichissements contextuels basés sur les caractéristiques du patient
    
    Args:
        symptoms (str): Symptômes du patient
        patient_age (int): Âge du patient
        patient_gender (str): Genre du patient
        
    Returns:
        str: Enrichissements contextuels
    """
    enhancements = []
    
    # Patterns spécifiques à l'âge
    if patient_age:
        if patient_age < 18:
            age_patterns = FeedbackPattern.objects.filter(
                description__icontains='pédiatrique',
                is_active=True
            )
        elif patient_age > 65:
            age_patterns = FeedbackPattern.objects.filter(
                description__icontains='gériatrique',
                is_active=True
            )
        else:
            age_patterns = FeedbackPattern.objects.none()
        
        if age_patterns.exists():
            age_section = f"\n👥 CONSIDÉRATIONS SPÉCIFIQUES ÂGE ({patient_age} ans):\n"
            for pattern in age_patterns[:3]:
                age_section += f"- {pattern.description}\n"
            enhancements.append(age_section)
    
    # Patterns spécifiques aux symptômes
    if symptoms:
        symptom_keywords = symptoms.lower().split()
        for keyword in symptom_keywords[:3]:  # Limiter à 3 mots-clés
            if len(keyword) > 3:  # Ignorer les mots trop courts
                symptom_patterns = FeedbackPattern.objects.filter(
                    description__icontains=keyword,
                    is_active=True
                )[:2]
                
                if symptom_patterns.exists():
                    symptom_section = f"\n🔍 PATTERNS POUR '{keyword.upper()}':\n"
                    for pattern in symptom_patterns:
                        symptom_section += f"- {pattern.description}\n"
                    enhancements.append(symptom_section)
    
    return "".join(enhancements)


def log_prompt_enhancement_usage(enhancement_type, patterns_used):
    """
    Log l'utilisation des enrichissements de prompt pour analyse
    
    Args:
        enhancement_type (str): Type d'enrichissement utilisé
        patterns_used (list): Liste des patterns utilisés
    """
    # Cette fonction peut être utilisée pour tracker l'efficacité
    # des différents types d'enrichissements
    pass


def get_prompt_enhancement_summary():
    """
    Retourne un résumé des enrichissements disponibles
    
    Returns:
        dict: Résumé des patterns disponibles par type
    """
    summary = {}
    
    for pattern_type, pattern_name in FeedbackPattern.PATTERN_TYPE_CHOICES:
        count = FeedbackPattern.objects.filter(
            pattern_type=pattern_type,
            is_active=True
        ).count()
        
        if count > 0:
            summary[pattern_name] = {
                'count': count,
                'latest': FeedbackPattern.objects.filter(
                    pattern_type=pattern_type,
                    is_active=True
                ).first()
            }
    
    return summary


def refresh_prompt_patterns():
    """
    Actualise les patterns de prompt en désactivant les anciens
    et en recalculant les scores de confiance
    """
    # Désactiver les patterns trop anciens (plus de 30 jours sans occurrence)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    old_patterns = FeedbackPattern.objects.filter(
        last_occurrence__lt=thirty_days_ago,
        is_active=True
    )
    
    deactivated_count = old_patterns.update(is_active=False)
    
    # Recalculer les scores de confiance basés sur la fréquence récente
    active_patterns = FeedbackPattern.objects.filter(is_active=True)
    
    for pattern in active_patterns:
        # Calculer le score basé sur la fréquence et la récence
        days_since_last = (timezone.now() - pattern.last_occurrence).days
        recency_factor = max(0, 1 - (days_since_last / 30))  # Diminue avec le temps
        
        # Nouveau score de confiance
        new_confidence = min(1.0, (pattern.frequency / 10) * recency_factor)
        pattern.confidence_score = new_confidence
        pattern.save()
    
    return {
        'deactivated_patterns': deactivated_count,
        'active_patterns': active_patterns.count(),
        'refreshed_at': timezone.now()
    }
