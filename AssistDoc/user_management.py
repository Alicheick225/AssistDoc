#!/usr/bin/env python
"""
Script de gestion des utilisateurs pour AssistDoc
Utilisation: python manage.py shell < user_management.py
"""

import os
import django
from django.contrib.auth.hashers import make_password

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AssistDoc.settings')
django.setup()

from app.models import User, Hospital

def create_doctor_user(username, password, email="", first_name="", last_name="", speciality=""):
    """Créer un utilisateur médecin"""
    try:
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            print(f"❌ L'utilisateur '{username}' existe déjà!")
            return None
        
        # Créer l'utilisateur
        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=make_password(password),  # Hash du mot de passe
            user_type='doctor',
            speciality=speciality,
            is_active=True,
            is_staff=False
        )
        
        print(f"✅ Utilisateur médecin '{username}' créé avec succès!")
        print(f"   - Email: {email}")
        print(f"   - Nom complet: {first_name} {last_name}")
        print(f"   - Spécialité: {speciality}")
        return user
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur: {e}")
        return None

def check_user_exists(username):
    """Vérifier si un utilisateur existe et afficher ses informations"""
    try:
        user = User.objects.get(username=username)
        print(f"✅ Utilisateur trouvé: {username}")
        print(f"   - ID: {user.id}")
        print(f"   - Email: {user.email}")
        print(f"   - Nom complet: {user.get_full_name()}")
        print(f"   - Type d'utilisateur: {user.user_type}")
        print(f"   - Actif: {user.is_active}")
        print(f"   - Staff: {user.is_staff}")
        print(f"   - Spécialité: {user.speciality}")
        print(f"   - Date de création: {user.date_joined}")
        return user
    except User.DoesNotExist:
        print(f"❌ Utilisateur '{username}' non trouvé!")
        return None

def reset_user_password(username, new_password):
    """Réinitialiser le mot de passe d'un utilisateur"""
    try:
        user = User.objects.get(username=username)
        user.password = make_password(new_password)
        user.save()
        print(f"✅ Mot de passe réinitialisé pour '{username}'")
        return True
    except User.DoesNotExist:
        print(f"❌ Utilisateur '{username}' non trouvé!")
        return False

def list_all_users():
    """Lister tous les utilisateurs"""
    users = User.objects.all()
    print(f"\n📋 Liste de tous les utilisateurs ({users.count()}):")
    print("-" * 80)
    for user in users:
        print(f"  🔹 {user.username} ({user.get_full_name()}) - Type: {user.user_type} - Actif: {user.is_active}")

def main():
    print("🏥 GESTIONNAIRE D'UTILISATEURS ASSISTDOC")
    print("=" * 50)
    
    # Vérifier si DrTape07 existe
    print("\n1. Vérification de l'utilisateur DrTape07:")
    user = check_user_exists("DrTape07")
    
    if not user:
        print("\n2. Création de l'utilisateur DrTape07:")
        user = create_doctor_user(
            username="DrTape07",
            password="motdepasse123",  # Changez ce mot de passe
            email="drtape07@example.com",
            first_name="Dr",
            last_name="Tape",
            speciality="Médecine Générale"
        )
    
    # Lister tous les utilisateurs
    print("\n3. Liste de tous les utilisateurs:")
    list_all_users()
    
    print("\n✅ Script terminé!")

if __name__ == "__main__":
    main()
