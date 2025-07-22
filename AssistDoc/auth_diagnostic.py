#!/usr/bin/env python
"""
Script de diagnostic d'authentification pour AssistDoc
"""

import os
import django
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AssistDoc.settings')
django.setup()

from app.models import User

def test_authentication(username, password):
    """Tester l'authentification d'un utilisateur"""
    print(f"🔍 Test d'authentification pour: {username}")
    print("-" * 50)
    
    # 1. Vérifier si l'utilisateur existe
    try:
        user = User.objects.get(username=username)
        print(f"✅ Utilisateur trouvé dans la base de données")
        print(f"   - ID: {user.id}")
        print(f"   - Username: {user.username}")
        print(f"   - Email: {user.email}")
        print(f"   - Type: {user.user_type}")
        print(f"   - Actif: {user.is_active}")
        print(f"   - Staff: {user.is_staff}")
        print(f"   - Superuser: {user.is_superuser}")
        
        # 2. Vérifier le mot de passe
        password_valid = check_password(password, user.password)
        print(f"\n🔐 Vérification du mot de passe:")
        print(f"   - Mot de passe valide: {password_valid}")
        
        if not password_valid:
            print(f"   ❌ Le mot de passe fourni ne correspond pas!")
            return False
        
        # 3. Vérifier l'authentification Django
        authenticated_user = authenticate(username=username, password=password)
        print(f"\n🔓 Test d'authentification Django:")
        if authenticated_user:
            print(f"   ✅ Authentification réussie!")
            print(f"   - Utilisateur authentifié: {authenticated_user.username}")
            
            # 4. Vérifier les conditions spécifiques de l'application
            print(f"\n🏥 Vérification des conditions de l'application:")
            if authenticated_user.user_type == 'doctor':
                print(f"   ✅ L'utilisateur est bien un médecin")
                return True
            else:
                print(f"   ❌ L'utilisateur n'est pas un médecin (type: {authenticated_user.user_type})")
                return False
        else:
            print(f"   ❌ Échec de l'authentification Django!")
            return False
            
    except User.DoesNotExist:
        print(f"❌ Utilisateur '{username}' non trouvé dans la base de données!")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    print("🔍 DIAGNOSTIC D'AUTHENTIFICATION ASSISTDOC")
    print("=" * 55)
    
    # Test avec DrTape07
    username = "DrTape07"
    password = "motdepasse123"  # Remplacez par le vrai mot de passe
    
    print(f"\n🎯 Test pour l'utilisateur: {username}")
    success = test_authentication(username, password)
    
    if success:
        print(f"\n✅ RÉSULTAT: L'authentification devrait fonctionner!")
    else:
        print(f"\n❌ RÉSULTAT: Problème d'authentification détecté!")
        print(f"\n💡 SOLUTIONS POSSIBLES:")
        print(f"   1. Vérifier que l'utilisateur existe")
        print(f"   2. Vérifier le mot de passe")
        print(f"   3. S'assurer que user_type = 'doctor'")
        print(f"   4. Vérifier que is_active = True")

if __name__ == "__main__":
    main()
