import json
import google.generativeai as genai
from django.conf import settings
from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Patient, Consultation, Symptom, Hospital, User
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from datetime import datetime



# Configuration de Gemini (assurez-vous que la clé est dans settings.py)
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
except Exception as e:
    print(f"Erreur de configuration de l'API Gemini : {e}")


@csrf_exempt  # Pour simplifier. En production, utilisez la gestion CSRF de Django.
@require_POST
def generer_prescription(request):
    """
    Reçoit les données du patient en JSON, les envoie à Gemini,
    et retourne la recommandation en JSON.
    """
    try:
        # 1. Récupérer les données du patient depuis le corps de la requête
        patient_data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"erreur": "JSON invalide dans la requête."}, status=400)

    # 2. Définir la configuration du modèle (traduite depuis votre code TypeScript)
    # Le 'systemInstruction' et le 'schema' sont identiques à votre app React
    system_instruction = """Tu es un système expert d'aide à la décision médicale spécialisé dans la prescription de médicaments. 
    Ton rôle est d'analyser les données cliniques d'un patient et de fournir des recommandations de prescription basées sur les meilleures pratiques médicales.
    
    IMPORTANT: Tu ne remplaces pas le jugement clinique d'un médecin. Tes recommandations sont des suggestions pour aider à la prise de décision.
    
    Analyse les données fournies et recommande des médicaments appropriés en tenant compte de:
    - L'âge, le poids et les conditions médicales du patient
    - Les allergies et contre-indications
    - Les interactions médicamenteuses potentielles
    - Les dosages appropriés selon les guidelines
    - Les effets secondaires possibles
    
    Fournis des justifications claires pour chaque recommandation."""
    
    # Le schéma de la réponse attendue
    prescription_schema = {
        'type': 'OBJECT',
        'properties': {
            'recommandations_prescription': {
                'type': 'ARRAY',
                'items': {
                    'type': 'OBJECT',
                    'properties': {
                        'nom_medicament': {'type': 'STRING'},
                        'posologie': {'type': 'STRING'},
                        'voie_administration': {'type': 'STRING'},
                        'justification': {'type': 'STRING'},
                        'effets_secondaires_cles': {'type': 'ARRAY', 'items': {'type': 'STRING'}},
                        'contre_indications_notables': {'type': 'ARRAY', 'items': {'type': 'STRING'}},
                        'interactions_medic_potentielles': {'type': 'STRING'},
                        'notes_supplementaires_ia': {'type': 'STRING'},
                    },
                    'required': ["nom_medicament", "posologie", "voie_administration", "justification"]
                }
            }
        },
        'required': ["recommandations_prescription"]
    }

    try:
        # Initialisation du modèle avec la configuration
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_instruction,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=prescription_schema
            )
        )

        # 3. Créer le prompt
        prompt = f"Voici les données du patient. Analyse-les et fournis tes recommandations de prescription.\n\n{json.dumps(patient_data, indent=2, ensure_ascii=False)}"

        # 4. Appeler l'API Gemini
        response = model.generate_content(prompt)
        
        # L'API retourne un texte qui est une chaîne JSON, on la parse en dictionnaire Python
        donnees_recommandation = json.loads(response.text)

        # 5. Renvoyer le résultat au frontend
        return JsonResponse(donnees_recommandation)

    except Exception as e:
        print(f"Erreur lors de l'appel à l'API Gemini : {e}")
        return JsonResponse(
            {"erreur": f"Une erreur est survenue lors de la communication avec le service d'IA: {str(e)}"},
            status=500
        )


@csrf_protect
@login_required
@require_POST
def traiter_consultation(request):
    """
    Traite le formulaire de consultation, récupère les données du patient et historique,
    envoie tout à Gemini pour obtenir diagnostic et prescriptions.
    """
    try:
        # Récupérer l'ID du patient depuis le formulaire
        patient_id = request.POST.get('patient_id')
        if not patient_id:
            messages.error(request, 'Patient non spécifié.')
            return redirect('consultation')
        
        # Récupérer le patient
        patient = get_object_or_404(Patient, id=patient_id)
        
        # Récupérer les données du formulaire de consultation
        consultation_data = {
            'consultation_reason': request.POST.get('consultation_reason', ''),
            'clinical_exam': request.POST.get('clinical_exam', ''),
            'symptoms_text': request.POST.get('symptoms_text', ''),
            'tension': request.POST.get('tension_arterielle', ''),
            'temperature': request.POST.get('temperature', ''),
            'heart_rate': request.POST.get('frequence_cardiaque', ''),
            'weight': request.POST.get('poids_kg', ''),
            'height': request.POST.get('taille_cm', ''),
            'oxygen_saturation': request.POST.get('saturation_o2', ''),
            'additional_notes': request.POST.get('additional_notes', ''),
        }
        
        # Récupérer l'historique des consultations du patient
        consultations_precedentes = Consultation.objects.filter(patient=patient).order_by('-consultation_date')[:5]
        
        # Construire les données complètes pour Gemini
        data_pour_gemini = {
            "patient": {
                "nom_complet": f"{patient.first_name} {patient.last_name}",
                "age": patient.birth_date.year if patient.birth_date else "Non spécifié",
                "sexe": patient.gender,
                "numero_securite_sociale": patient.social_security_number,
                "allergies": patient.allergies or "Aucune allergie connue",
                "antecedents_medicaux": {
                    "maladies": patient.diseases or "Aucune maladie connue",
                    "chirurgies": patient.surgeries or "Aucune chirurgie",
                    "vaccinations": patient.vaccines or "Historique vaccinal non disponible",
                    "medicaments_actuels": patient.actual_medecines or "Aucun médicament actuel"
                }
            },
            "consultation_actuelle": {
                "motif_consultation": consultation_data['consultation_reason'],
                "examen_clinique": consultation_data['clinical_exam'],
                "symptomes_decrits": consultation_data['symptoms_text'],
                "signes_vitaux": {
                    "tension_arterielle": consultation_data['tension'],
                    "temperature": consultation_data['temperature'],
                    "frequence_cardiaque": consultation_data['heart_rate'],
                    "poids": consultation_data['weight'],
                    "taille": consultation_data['height'],
                    "saturation_oxygene": consultation_data['oxygen_saturation']
                },
                "notes_supplementaires": consultation_data['additional_notes']
            },
            "historique_consultations": []
        }
        
        # Ajouter l'historique des consultations
        for consultation in consultations_precedentes:
            data_pour_gemini["historique_consultations"].append({
                "date": consultation.consultation_date.strftime("%Y-%m-%d"),
                "motif": consultation.consultation_reason,
                "diagnostic": consultation.initial_diagnosis or "Non spécifié",
                "signes_vitaux": {
                    "tension": str(consultation.tension) if consultation.tension else None,
                    "temperature": str(consultation.temperature) if consultation.temperature else None,
                    "frequence_cardiaque": consultation.heart_rate if consultation.heart_rate else None
                }
            })
        
        # Configuration du modèle Gemini pour diagnostic et prescription
        base_system_instruction = """Tu es un médecin expert spécialisé dans le diagnostic médical et la prescription de médicaments. 
        Ton rôle est d'analyser les données complètes d'un patient incluant ses antécédents, la consultation actuelle et l'historique médical pour fournir:
        
        1. UN DIAGNOSTIC DÉTAILLÉ avec diagnostic différentiel
        2. DES RECOMMANDATIONS DE PRESCRIPTION spécifiques et justifiées
        3. DES RECOMMANDATIONS DE SUIVI
        
        IMPORTANT: 
        - Tes recommandations sont des suggestions pour aider le médecin dans sa prise de décision
        - Considère toujours les allergies, antécédents et interactions médicamenteuses
        - Fournis des justifications médicales claires
        - Propose des alternatives si nécessaire
        
        Analyse TOUTES les données fournies: patient, consultation actuelle, et historique médical."""
        
        # 🚀 NOUVEAU: Enrichir le prompt avec les patterns de feedback
        try:
            from .prompt_enhancement import get_enhanced_system_instruction, get_contextual_enhancements
            from django.utils import timezone as django_timezone
            
            # Enrichissement principal basé sur les patterns globaux
            enhanced_instruction = get_enhanced_system_instruction(base_system_instruction)
            
            # Enrichissement contextuel basé sur le patient
            contextual_enhancements = get_contextual_enhancements(
                symptoms=consultation_data['symptoms_text'],
                patient_age=django_timezone.now().year - patient.birth_date.year if patient.birth_date else None,
                patient_gender=patient.gender
            )
            
            system_instruction = enhanced_instruction + contextual_enhancements
            
        except Exception as e:
            # Fallback vers l'instruction de base en cas d'erreur
            print(f"Erreur lors de l'enrichissement du prompt: {e}")
            system_instruction = base_system_instruction
        
        prescription_schema = {
            'type': 'OBJECT',
            'properties': {
                'diagnostic_principal': {'type': 'STRING'},
                'diagnostic_differentiel': {
                    'type': 'ARRAY',
                    'items': {'type': 'STRING'}
                },
                'justification_diagnostic': {'type': 'STRING'},
                'prescriptions_recommandees': {
                    'type': 'ARRAY',
                    'items': {
                        'type': 'OBJECT',
                        'properties': {
                            'nom_medicament': {'type': 'STRING'},
                            'dosage': {'type': 'STRING'},
                            'frequence': {'type': 'STRING'},
                            'duree_traitement': {'type': 'STRING'},
                            'voie_administration': {'type': 'STRING'},
                            'justification': {'type': 'STRING'},
                            'precautions': {'type': 'STRING'},
                            'effets_secondaires_surveiller': {
                                'type': 'ARRAY',
                                'items': {'type': 'STRING'}
                            }
                        },
                        'required': ['nom_medicament', 'dosage', 'frequence', 'justification']
                    }
                },
                'examens_complementaires': {
                    'type': 'ARRAY',
                    'items': {'type': 'STRING'}
                },
                'recommandations_suivi': {'type': 'STRING'},
                'conseils_patient': {'type': 'STRING'},
                'urgence_niveau': {
                    'type': 'STRING',
                    'enum': ['Faible', 'Modéré', 'Élevé', 'Urgent']
                }
            },
            'required': ['diagnostic_principal', 'justification_diagnostic', 'prescriptions_recommandees']
        }
        
        # Créer le modèle Gemini
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_instruction,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=prescription_schema
            )
        )
        
        # Créer le prompt détaillé
        prompt = f"""Analyse complète du patient et recommandations médicales:

{json.dumps(data_pour_gemini, indent=2, ensure_ascii=False)}

Fournis une analyse complète avec diagnostic et prescriptions détaillées basées sur toutes ces données."""
        
        # Appeler Gemini
        response = model.generate_content(prompt)
        recommendations = json.loads(response.text)
        
        # Sauvegarder la consultation dans la base de données
        nouvelle_consultation = Consultation.objects.create(
            patient=patient,
            hospital=request.user.hospitals.first() if request.user.hospitals.exists() else None,
            doctor=request.user,
            consultation_reason=consultation_data['consultation_reason'],
            clinical_exam=consultation_data['clinical_exam'],
            initial_diagnosis=recommendations.get('diagnostic_principal', ''),
            tension=float(consultation_data['tension'].replace('/', '.').split('/')[0]) if consultation_data['tension'] else None,
            temperature=float(consultation_data['temperature'].replace('°C', '')) if consultation_data['temperature'] else None,
            heart_rate=int(consultation_data['heart_rate'].replace('bpm', '').strip()) if consultation_data['heart_rate'] else None,
            weight=float(consultation_data['weight']) if consultation_data['weight'] else None,
            height=float(consultation_data['height']) if consultation_data['height'] else None,
            oxygen_saturation=float(consultation_data['oxygen_saturation'].replace('%', '')) if consultation_data['oxygen_saturation'] else None,
        )
        
        # Retourner la page de résultats avec les recommandations
        context = {
            'patient': patient,
            'consultation': nouvelle_consultation,
            'recommendations': recommendations,
            'consultation_data': consultation_data
        }
        
        return render(request, 'consultation_results.html', context)
        
    except Exception as e:
        print(f"Erreur lors du traitement de la consultation: {e}")
        messages.error(request, f'Une erreur est survenue: {str(e)}')
        return redirect('consultation')


def index(request):
    return render(request, 'index.html')

@csrf_protect
def login_page(request):
    # Rediriger si l'utilisateur est déjà connecté
    #if request.user.is_authenticated:
       #  return redirect("dashboard")
    
    if request.method == "POST":
        # Récupérer les données du formulaire
        username = request.POST.get("username")  # Plus clair
        password = request.POST.get("password")
        
        # Validation des champs
        if not username or not password:
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'login.html')
        
        print(f"Tentative de connexion pour: {username}")  # Debug
        
        # Vérifier d'abord si l'utilisateur existe
        try:
            from .models import User
            user_exists = User.objects.filter(username=username).exists()
            if not user_exists:
                print(f"Utilisateur '{username}' non trouvé dans la base de données")
                messages.error(request, 'Utilisateur non trouvé. Vérifiez votre nom d\'utilisateur.')
                return render(request, 'login.html')
            
            # Récupérer l'utilisateur pour vérifier ses propriétés
            user_obj = User.objects.get(username=username)
            print(f"Utilisateur trouvé - Type: {user_obj.user_type}, Actif: {user_obj.is_active}")
            
            # Vérifier si c'est un médecin avant l'authentification
            if user_obj.user_type != 'doctor':
                print(f"Utilisateur '{username}' n'est pas un médecin (type: {user_obj.user_type})")
                messages.error(request, 'Accès réservé aux médecins uniquement.')
                return render(request, 'login.html')
            
            # Vérifier si l'utilisateur est actif
            if not user_obj.is_active:
                print(f"Utilisateur '{username}' est inactif")
                messages.error(request, 'Votre compte est désactivé. Contactez l\'administrateur.')
                return render(request, 'login.html')
                
        except Exception as e:
            print(f"Erreur lors de la vérification de l'utilisateur: {e}")
            messages.error(request, 'Erreur lors de la vérification. Contactez l\'administrateur.')
            return render(request, 'login.html')
        
        # Authentification
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            print(f"Authentification réussie pour: {user.username}")
            login(request, user)
            messages.success(request, f'Bienvenue Dr. {user.get_full_name() or user.username}')
            
            # Redirection vers la page demandée ou dashboard par défaut
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            print(f"Échec d'authentification pour: {username}")  # Debug
            messages.error(request, 'Mot de passe incorrect. Vérifiez votre mot de passe.')
    
    return render(request, 'login.html')

def dashboard(request):
    numero = request.GET.get('numero', '').strip()

    if numero.isdigit():
        patients = Patient.objects.filter(social_security_number=numero)
    else:
        patients = Patient.objects.all()

    context = {
        'patients': patients,
    }
    return render(request, 'dashboard.html', context)

def consultation(request):
    return render(request, 'consultation.html')

def symptome(request, patient_social_security_number):
    patient = get_object_or_404(Patient, social_security_number=patient_social_security_number)
    
    # Vérifier si on veut éditer une consultation existante
    edit_consultation_id = request.GET.get('edit')
    edit_consultation = None
    if edit_consultation_id:
        try:
            edit_consultation = Consultation.objects.get(id=edit_consultation_id, patient=patient)
        except Consultation.DoesNotExist:
            messages.error(request, 'Consultation non trouvée.')
    
    if request.method == 'POST':
        # Appeler directement la logique de traitement de consultation
        try:
            # Récupérer les données du formulaire de consultation
            consultation_data = {
                'consultation_reason': request.POST.get('consultation_reason', ''),
                'clinical_exam': request.POST.get('clinical_exam', ''),
                'symptoms_text': request.POST.get('symptoms_text', ''),
                'tension': request.POST.get('tension_arterielle', ''),
                'temperature': request.POST.get('temperature', ''),
                'heart_rate': request.POST.get('frequence_cardiaque', ''),
                'weight': request.POST.get('poids_kg', ''),
                'height': request.POST.get('taille_cm', ''),
                'oxygen_saturation': request.POST.get('saturation_o2', ''),
                'additional_notes': request.POST.get('additional_notes', ''),
            }
            
            # Récupérer l'historique des consultations du patient
            consultations_precedentes = Consultation.objects.filter(patient=patient).order_by('-consultation_date')[:5]
            
            # Construire les données complètes pour Gemini
            data_pour_gemini = {
                "patient": {
                    "nom_complet": f"{patient.first_name} {patient.last_name}",
                    "age": patient.birth_date.year if patient.birth_date else "Non spécifié",
                    "sexe": patient.gender,
                    "numero_securite_sociale": patient.social_security_number,
                    "allergies": patient.allergies or "Aucune allergie connue",
                    "antecedents_medicaux": {
                        "maladies": patient.diseases or "Aucune maladie connue",
                        "chirurgies": patient.surgeries or "Aucune chirurgie",
                        "vaccinations": patient.vaccines or "Historique vaccinal non disponible",
                        "medicaments_actuels": patient.actual_medecines or "Aucun médicament actuel"
                    }
                },
                "consultation_actuelle": {
                    "motif_consultation": consultation_data['consultation_reason'],
                    "examen_clinique": consultation_data['clinical_exam'],
                    "symptomes_decrits": consultation_data['symptoms_text'],
                    "signes_vitaux": {
                        "tension_arterielle": consultation_data['tension'],
                        "temperature": consultation_data['temperature'],
                        "frequence_cardiaque": consultation_data['heart_rate'],
                        "poids": consultation_data['weight'],
                        "taille": consultation_data['height'],
                        "saturation_oxygene": consultation_data['oxygen_saturation']
                    },
                    "notes_supplementaires": consultation_data['additional_notes']
                },
                "historique_consultations": []
            }
            
            # Ajouter l'historique des consultations
            for consultation in consultations_precedentes:
                data_pour_gemini["historique_consultations"].append({
                    "date": consultation.consultation_date.strftime("%Y-%m-%d"),
                    "motif": consultation.consultation_reason,
                    "diagnostic": consultation.initial_diagnosis or "Non spécifié",
                    "signes_vitaux": {
                        "tension": str(consultation.tension) if consultation.tension else None,
                        "temperature": str(consultation.temperature) if consultation.temperature else None,
                        "frequence_cardiaque": consultation.heart_rate if consultation.heart_rate else None
                    }
                })
            
            # Configuration du modèle Gemini pour diagnostic et prescription
            system_instruction = """Tu es un médecin expert spécialisé dans le diagnostic médical et la prescription de médicaments. 
            Ton rôle est d'analyser les données complètes d'un patient incluant ses antécédents, la consultation actuelle et l'historique médical pour fournir:
            
            1. UN DIAGNOSTIC DÉTAILLÉ avec diagnostic différentiel
            2. DES RECOMMANDATIONS DE PRESCRIPTION spécifiques et justifiées
            3. UNE ORDONNANCE MÉDICALE FORMELLE avec médicaments détaillés
            4. DES RECOMMANDATIONS DE SUIVI
            
            IMPORTANT: 
            - Tes recommandations sont des suggestions pour aider le médecin dans sa prise de décision
            - Considère toujours les allergies, antécédents et interactions médicamenteuses
            - Fournis des justifications médicales claires
            - Pour l'ordonnance, propose des médicaments avec posologie précise, fréquence et durée
            - Inclus des instructions claires pour le patient
            - Propose des alternatives si nécessaire
            
            Analyse TOUTES les données fournies: patient, consultation actuelle, et historique médical.
            
            L'ordonnance doit être complète et prête à être utilisée par le médecin."""
            
            prescription_schema = {
                'type': 'OBJECT',
                'properties': {
                    'diagnostic_principal': {'type': 'STRING'},
                    'diagnostic_differentiel': {
                        'type': 'ARRAY',
                        'items': {'type': 'STRING'}
                    },
                    'justification_diagnostic': {'type': 'STRING'},
                    'prescriptions_recommandees': {
                        'type': 'ARRAY',
                        'items': {
                            'type': 'OBJECT',
                            'properties': {
                                'nom_medicament': {'type': 'STRING'},
                                'dosage': {'type': 'STRING'},
                                'frequence': {'type': 'STRING'},
                                'duree_traitement': {'type': 'STRING'},
                                'voie_administration': {'type': 'STRING'},
                                'justification': {'type': 'STRING'},
                                'precautions': {'type': 'STRING'},
                                'effets_secondaires_surveiller': {
                                    'type': 'ARRAY',
                                    'items': {'type': 'STRING'}
                                }
                            },
                            'required': ['nom_medicament', 'dosage', 'frequence', 'justification']
                        }
                    },
                    'examens_complementaires': {
                        'type': 'ARRAY',
                        'items': {'type': 'STRING'}
                    },
                    'recommandations_suivi': {'type': 'STRING'},
                    'conseils_patient': {'type': 'STRING'},
                    'urgence_niveau': {
                        'type': 'STRING',
                        'enum': ['Faible', 'Modéré', 'Élevé', 'Urgent']
                    },
                    'ordonnance_medicale': {
                        'type': 'OBJECT',
                        'properties': {
                            'medicaments': {
                                'type': 'ARRAY',
                                'items': {
                                    'type': 'OBJECT',
                                    'properties': {
                                        'nom_commercial': {'type': 'STRING'},
                                        'nom_generique': {'type': 'STRING'},
                                        'forme': {'type': 'STRING'},  # comprimé, gélule, sirop, etc.
                                        'dosage_unitaire': {'type': 'STRING'},  # ex: 500mg
                                        'posologie': {'type': 'STRING'},  # ex: 1 comprimé
                                        'frequence': {'type': 'STRING'},  # ex: 3 fois par jour
                                        'duree': {'type': 'STRING'},  # ex: 7 jours
                                        'moment_prise': {'type': 'STRING'},  # ex: avant les repas
                                        'instructions_speciales': {'type': 'STRING'}
                                    },
                                    'required': ['nom_commercial', 'posologie', 'frequence', 'duree']
                                }
                            },
                            'instructions_generales': {'type': 'STRING'},
                            'contre_indications': {'type': 'STRING'},
                            'renouvellement': {'type': 'STRING'},  # ex: "Non renouvelable" ou "Renouvelable 2 fois"
                            'duree_validite': {'type': 'STRING'}  # ex: "3 mois"
                        },
                        'required': ['medicaments', 'instructions_generales']
                    }
                },
                'required': ['diagnostic_principal', 'justification_diagnostic', 'prescriptions_recommandees', 'ordonnance_medicale']
            }
            
            # Créer le modèle Gemini
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=system_instruction,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=prescription_schema
                )
            )
            
            # Créer le prompt détaillé
            prompt = f"""Analyse complète du patient et recommandations médicales:

{json.dumps(data_pour_gemini, indent=2, ensure_ascii=False)}

Fournis une analyse complète avec diagnostic et prescriptions détaillées basées sur toutes ces données."""
            
            # Appeler Gemini
            response = model.generate_content(prompt)
            recommendations = json.loads(response.text)
            
            # Sauvegarder la consultation dans la base de données
            nouvelle_consultation = Consultation.objects.create(
                patient=patient,
                hospital=request.user.hospitals.first() if request.user.hospitals.exists() else None,
                doctor=request.user,
                consultation_reason=consultation_data['consultation_reason'],
                clinical_exam=consultation_data['clinical_exam'],
                initial_diagnosis=recommendations.get('diagnostic_principal', ''),
                tension=float(consultation_data['tension'].replace('/', '.').split('/')[0]) if consultation_data['tension'] else None,
                temperature=float(consultation_data['temperature']) if consultation_data['temperature'] else None,
                heart_rate=int(consultation_data['heart_rate']) if consultation_data['heart_rate'] else None,
                weight=float(consultation_data['weight']) if consultation_data['weight'] else None,
                height=float(consultation_data['height']) if consultation_data['height'] else None,
                oxygen_saturation=float(consultation_data['oxygen_saturation']) if consultation_data['oxygen_saturation'] else None,
                gemini_recommendations=recommendations,  # Stocker les recommandations Gemini
            )
            
            # Retourner la page de résultats avec les recommandations
            context = {
                'patient': patient,
                'consultation': nouvelle_consultation,
                'recommendations': recommendations,
                'consultation_data': consultation_data
            }
            
            return render(request, 'consultation_results.html', context)
            
        except Exception as e:
            print(f"Erreur lors du traitement de la consultation: {e}")
            messages.error(request, f'Une erreur est survenue: {str(e)}')
            return render(request, 'symptome.html', {'patient': patient})
    
    # Préparer le contexte avec les données d'édition si nécessaire
    context = {
        'patient': patient,
        'edit_consultation': edit_consultation
    }
    return render(request, 'symptome.html', context)

@csrf_protect
@login_required
@require_POST
def valider_consultation(request, consultation_id):
    """
    Valide une consultation et l'ajoute définitivement à l'historique
    Crée automatiquement un feedback pour l'IA
    """
    try:
        consultation = get_object_or_404(Consultation, id=consultation_id, doctor=request.user)
        
        # Marquer la consultation comme validée
        consultation.is_validated = True
        consultation.save()
        
        # Créer automatiquement un feedback de base
        from .models import PrescriptionFeedback
        
        # Vérifier si un feedback existe déjà
        if not hasattr(consultation, 'feedback'):
            # Déterminer le type de feedback selon l'historique
            feedback_type = 'validee_directement'  # Par défaut
            
            # Si des modifications ont été apportées, détecter cela via la consultation
            # (Vous pourrez améliorer cette logique selon vos besoins)
            if request.POST.get('was_modified') == 'true':
                feedback_type = 'modifiee'
            
            feedback = PrescriptionFeedback.objects.create(
                consultation=consultation,
                doctor=request.user,
                feedback_type=feedback_type,
                pertinence_diagnostic=8,  # Score par défaut - peut être modifié plus tard
                pertinence_prescription=8,  # Score par défaut - peut être modifié plus tard
                commentaires_medecin="Validation automatique lors de la validation de consultation"
            )
            
            messages.success(request, 'Consultation validée et feedback créé pour l\'amélioration de l\'IA.')
        else:
            messages.success(request, 'Consultation validée avec succès.')
        
        return redirect('dashboard')
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la validation: {str(e)}')
        return redirect('dashboard')

@csrf_protect
@login_required
def modifier_prescription(request, consultation_id):
    """
    Permet de modifier la prescription générée par l'IA
    """
    try:
        consultation = get_object_or_404(Consultation, id=consultation_id, doctor=request.user)
        
        if request.method == 'POST':
            # Récupérer les données modifiées du formulaire
            prescriptions_text = request.POST.get('prescriptions_recommandees', '')
            
            # Convertir le texte des prescriptions en format structuré
            prescriptions_structurees = []
            if prescriptions_text.strip():
                # Diviser le texte par lignes pour traiter chaque médicament
                lignes = prescriptions_text.strip().split('\n')
                medicament_actuel = {}
                
                for ligne in lignes:
                    ligne = ligne.strip()
                    if ligne and (ligne[0].isdigit() or ligne.startswith('-')):
                        # Si c'est une nouvelle entrée de médicament (commence par un numéro)
                        if ligne[0].isdigit():
                            # Sauvegarder le médicament précédent s'il existe
                            if medicament_actuel:
                                prescriptions_structurees.append(medicament_actuel)
                            
                            # Nouveau médicament
                            nom_medicament = ligne.split('.', 1)[1].strip() if '.' in ligne else ligne
                            medicament_actuel = {
                                'nom_medicament': nom_medicament,
                                'dosage': '',
                                'frequence': '',
                                'duree_traitement': '',
                                'justification': '',
                                'voie_administration': 'Orale'
                            }
                        else:
                            # C'est une ligne de détail (dosage, fréquence, etc.)
                            if 'Dosage:' in ligne:
                                medicament_actuel['dosage'] = ligne.split('Dosage:')[1].strip()
                            elif 'Fréquence:' in ligne:
                                medicament_actuel['frequence'] = ligne.split('Fréquence:')[1].strip()
                            elif 'Durée:' in ligne:
                                medicament_actuel['duree_traitement'] = ligne.split('Durée:')[1].strip()
                            elif 'Justification:' in ligne:
                                medicament_actuel['justification'] = ligne.split('Justification:')[1].strip()
                
                # Ajouter le dernier médicament
                if medicament_actuel:
                    prescriptions_structurees.append(medicament_actuel)
            
            # Structure des recommandations modifiées
            recommendations_modifiees = {
                'diagnostic_principal': request.POST.get('diagnostic_principal', ''),
                'justification_diagnostic': request.POST.get('justification_diagnostic', ''),
                'prescriptions_recommandees': prescriptions_structurees,  # Format structuré
                'recommandations_suivi': request.POST.get('recommandations_suivi', ''),
                'conseils_patient': request.POST.get('conseils_patient', ''),
                'urgence_niveau': request.POST.get('urgence_niveau', 'Faible'),
                'ordonnance_medicale': {
                    'instructions_generales': request.POST.get('instructions_generales', ''),
                    'medicaments': prescriptions_structurees,  # Utiliser la même structure
                    'contre_indications': request.POST.get('contre_indications', ''),
                    'renouvellement': request.POST.get('renouvellement', 'Non renouvelable'),
                    'duree_validite': request.POST.get('duree_validite', '3 mois')
                }
            }
            
            # Sauvegarder les modifications dans la consultation
            original_recommendations = consultation.gemini_recommendations.copy() if consultation.gemini_recommendations else {}
            consultation.gemini_recommendations = recommendations_modifiees
            consultation.initial_diagnosis = recommendations_modifiees['diagnostic_principal']
            consultation.save()
            
            # Créer ou mettre à jour le feedback pour les modifications
            from .models import PrescriptionFeedback
            
            try:
                # Vérifier si un feedback existe déjà
                if hasattr(consultation, 'feedback'):
                    feedback = consultation.feedback
                    feedback.feedback_type = 'modifiee'
                    feedback.modifications_effectuees = f"Prescription modifiée le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
                    feedback.raison_modification = request.POST.get('raison_modification', 'Modifications par le médecin')
                    feedback.save()
                else:
                    # Créer un nouveau feedback
                    feedback = PrescriptionFeedback.objects.create(
                        consultation=consultation,
                        doctor=request.user,
                        feedback_type='modifiee',
                        modifications_effectuees=f"Prescription modifiée le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
                        raison_modification=request.POST.get('raison_modification', 'Modifications par le médecin'),
                        pertinence_diagnostic=7,  # Score par défaut pour les modifications
                        pertinence_prescription=7,  # Score par défaut pour les modifications
                        commentaires_medecin="Feedback automatique - prescription modifiée"
                    )
                
                messages.success(request, 'Prescription modifiée avec succès. Feedback enregistré pour l\'amélioration de l\'IA.')
            except Exception as e:
                messages.warning(request, f'Prescription modifiée, mais erreur lors de l\'enregistrement du feedback: {str(e)}')
            
            # Retourner vers la page de résultats avec les modifications
            context = {
                'patient': consultation.patient,
                'consultation': consultation,
                'recommendations': recommendations_modifiees,
                'is_modified': True
            }
            return render(request, 'consultation_results.html', context)
            
        # Si GET, afficher le formulaire de modification avec les données existantes
        recommendations = consultation.gemini_recommendations or {}
        
        context = {
            'consultation': consultation,
            'patient': consultation.patient,
            'recommendations': recommendations
        }
        return render(request, 'modifier_prescription.html', context)
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la modification: {str(e)}')
        return redirect('dashboard')

@csrf_protect
@login_required
@require_POST
def supprimer_consultation(request, consultation_id):
    """
    Supprime une consultation spécifique
    """
    try:
        consultation = get_object_or_404(Consultation, id=consultation_id, doctor=request.user)
        patient = consultation.patient
        consultation.delete()
        messages.success(request, 'Consultation supprimée avec succès.')
        return redirect('dashboard')
    except Exception as e:
        messages.error(request, f'Erreur lors de la suppression: {str(e)}')
        return redirect('dashboard')

def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    
    # Récupérer toutes les consultations validées de ce patient, triées par date décroissante
    consultations_validees = Consultation.objects.filter(
        patient=patient, 
        is_validated=True
    ).order_by('-consultation_date')
    
    context = {
        'patient': patient,
        'consultations_validees': consultations_validees,
    }
    return render(request, 'patient_detail.html', context)

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

@csrf_protect
@login_required
@require_POST
def annuler_prescription(request, consultation_id):
    """
    Marque une prescription comme annulée/rejetée
    """
    try:
        consultation = get_object_or_404(Consultation, id=consultation_id, doctor=request.user)
        
        # Créer ou mettre à jour le feedback pour indiquer l'annulation
        from .models import PrescriptionFeedback
        
        feedback, created = PrescriptionFeedback.objects.get_or_create(
            consultation=consultation,
            doctor=request.user,
            defaults={
                'feedback_type': 'annulee',
                'pertinence_diagnostic': 3,  # Score plus faible car annulée
                'pertinence_prescription': 3,
                'commentaires_medecin': 'Prescription annulée par le médecin'
            }
        )
        
        if not created:
            feedback.feedback_type = 'annulee'
            feedback.save()
        
        # Marquer la consultation comme non validée
        consultation.is_validated = False
        consultation.save()
        
        messages.success(request, 'Prescription annulée. Feedback enregistré pour l\'amélioration de l\'IA.')
        return redirect('dashboard')
        
    except Exception as e:
        messages.error(request, f'Erreur lors de l\'annulation: {str(e)}')
        return redirect('dashboard')



