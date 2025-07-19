import json
import google.generativeai as genai
from django.conf import settings
from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Patient



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


def index(request):
    return render(request, 'index.html')

def login_page(request):
    return render(request, 'login.html')

def dashboard(request):
    numero = request.GET.get('numero', '').strip()

    if numero.isdigit():
        patients = Patient.objects.filter(numero_securite_sociale=numero)
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
    return render(request, 'symptome.html', {'patient': patient})

def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'patient_detail.html', {'patient': patient})



