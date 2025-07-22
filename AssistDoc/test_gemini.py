import os
import google.generativeai as genai
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_gemini_api():
    # Récupérer la clé API
    api_key = os.getenv('GEMINI_API_KEY')
    print(f"Clé API trouvée: {api_key is not None}")
    print(f"Clé API: {api_key[:10]}..." if api_key else "Aucune clé API")
    
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        print("❌ La clé API Gemini n'est pas configurée correctement.")
        print("Veuillez:")
        print("1. Aller sur https://aistudio.google.com/app/apikey")
        print("2. Créer une clé API gratuite")
        print("3. Remplacer YOUR_GEMINI_API_KEY dans le fichier .env")
        return False
    
    try:
        # Configurer Gemini
        genai.configure(api_key=api_key)
        
        # Test simple
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Dis juste 'Bonjour' pour tester l'API")
        
        print("✅ API Gemini fonctionne correctement!")
        print(f"Réponse de test: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur avec l'API Gemini: {e}")
        return False

if __name__ == "__main__":
    test_gemini_api()
