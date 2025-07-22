# 📋 README - AssistDoc IA Enhancement System

## 🎯 Vue d'ensemble

**AssistDoc** est un système d'assistance médicale intelligent utilisant l'IA Gemini 1.5 pour la génération de prescriptions médicales, enrichi d'un **système d'amélioration continue** basé sur le feedback des médecins.

### 🚀 Nouvelles fonctionnalités IA

- ✨ **Feedback automatique** lors de chaque validation/modification/annulation
- 📊 **Dashboard analytics** avec graphiques en temps réel  
- 🤖 **Système d'apprentissage** pour améliorer les prescriptions IA
- 📈 **Métriques de performance** calculées automatiquement
- 🎯 **Interface intuitive** pour les retours médecins

---

## 🏗️ Architecture Technique

### Stack Principal
- **Backend :** Django 5.2.4 + Python 3.10+
- **IA :** Google Gemini 1.5-flash  
- **Base de données :** SQLite/PostgreSQL
- **Frontend :** Tailwind CSS + Chart.js
- **API :** Django REST + JSON responses

### Nouveaux Modèles
```python
PrescriptionFeedback    # Retours médecins sur les prescriptions IA
AILearningData         # Données d'apprentissage anonymisées  
IAPerformanceMetrics   # Métriques de performance calculées
```

---

## ⚡ Installation Rapide

### 1. Configuration des Variables d'Environnement

1. Copiez le fichier `.env.example` vers `.env` :
   ```bash
   copy .env.example .env
   ```

2. Modifiez le fichier `.env` avec vos vraies valeurs :
   ```env
   # Votre clé API Gemini
   GEMINI_API_KEY=votre_vraie_cle_api_gemini

   # Configuration de votre base de données
   DB_NAME=votre_nom_de_base
   DB_USER=votre_utilisateur
   DB_PASSWORD=votre_mot_de_passe
   DB_HOST=votre_host
   DB_PORT=votre_port

   # Votre clé secrète Django
   SECRET_KEY=votre_cle_secrete_django
   ```

### 2. Installation des dépendances

```bash
# Activer l'environnement virtuel
env\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

Ou utilisez le script automatique :
```bash
install.bat
```

### 3. Migrations de la base de données (incluant nouvelles tables IA)

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

### 5. Lancer le serveur

```bash
python manage.py runserver
# Accès: http://127.0.0.1:8000
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| 📚 [**Documentation Complète**](DOCUMENTATION_SYSTEME_IA.md) | Guide complet du système d'amélioration IA |
| 🚀 [**Guide de Démarrage**](GUIDE_DEMARRAGE_RAPIDE.md) | Installation et test en 5 minutes |
| � [**Intégration Gemini**](INTEGRATION_GEMINI_FEEDBACK.md) | Comment les feedbacks remontent à Gemini |
| 💻 [**Guide Technique**](GUIDE_TECHNIQUE.md) | Architecture et implémentation détaillée |

---

## 🎮 Utilisation

### Pour les Médecins

1. **📝 Générer une prescription**
   ```
   Dashboard → Sélectionner patient → Nouvelle consultation → Générer prescription IA
   ```

2. **✅ Actions sur prescription**
   - **Valider** → Feedback automatique positif
   - **Modifier** → Feedback avec tracking des changements
   - **Annuler** → Feedback négatif pour apprentissage
   - **Feedback détaillé** → Interface complète de notation

3. **📊 Suivi traitement**
   - Noter l'efficacité observée (1-10)
   - Indiquer durée de guérison
   - Évaluer satisfaction patient

### Pour les Administrateurs

1. **⚙️ Interface d'administration**
   ```
   http://127.0.0.1:8000/admin/
   ```

2. **📈 Dashboard Analytics**
   ```
   Admin → IA Performance Metrics → Analytics
   ```

3. **🔄 Calcul des métriques**
   ```bash
   python manage.py calculate_ai_metrics
   ```

---

## 📊 Métriques de Performance

### Indicateurs Clés
- 🎯 **Taux de validation directe** (objectif: >70%)
- ✏️ **Taux de modification** (objectif: <25%)  
- ❌ **Taux de rejet** (objectif: <5%)
- ⭐ **Score moyen diagnostic** (objectif: >8.0/10)
- ⭐ **Score moyen prescription** (objectif: >8.0/10)

### Visualisations
- 📈 Graphiques d'évolution temporelle
- 🥧 Répartitions par type de feedback  
- 📊 Métriques en temps réel
- 🎯 Tableaux de bord interactifs

---

## 🛠️ Commandes Système IA

### Nouvelles commandes
```bash
# Calcul des métriques quotidiennes
python manage.py calculate_ai_metrics

# Calcul pour date spécifique  
python manage.py calculate_ai_metrics --date 2025-07-20

# Vérifier les feedbacks
python manage.py shell -c "from app.models import PrescriptionFeedback; print(f'Total feedbacks: {PrescriptionFeedback.objects.count()}')"
```

---

## 🎯 Nouvelles Fonctionnalités IA

### ✨ Système de Feedback Intelligent
- 🤖 Création automatique lors des actions
- ⭐ Notation par étoiles (1-10)
- 📝 Commentaires textuels détaillés
- 🎯 Suivi d'efficacité des traitements

### 📊 Analytics Avancés  
- 📈 Graphiques Chart.js interactifs
- 📊 Métriques en temps réel
- 🎯 Tableaux de bord personnalisés
- 📉 Tendances d'amélioration

### 🔄 Apprentissage Automatique
- 📚 Génération de données d'entraînement
- 🎯 Anonymisation automatique
- 📈 Amélioration continue des modèles
- 🤖 Optimisation des prescriptions

---

## 🔗 Liens Utiles

| Ressource | URL |
|-----------|-----|
| 🏥 **Application** | http://127.0.0.1:8000 |
| ⚙️ **Admin** | http://127.0.0.1:8000/admin |
| 📊 **Analytics IA** | http://127.0.0.1:8000/admin/app/iaperformancemetrics/analytics/ |
| 👥 **Dashboard** | http://127.0.0.1:8000/dashboard |

---

## 📞 Support

- 📧 **Email :** support@assistdoc.com
- 📖 **Documentation :** Voir fichiers DOCUMENTATION_SYSTEME_IA.md et GUIDE_DEMARRAGE_RAPIDE.md
- 🐛 **Issues :** Créer un ticket GitHub
- 💬 **Chat :** Support en ligne

---

## 🏷️ Version

**Version :** 1.0.0 - Système IA d'Amélioration  
**Date :** 20 juillet 2025  
**Status :** Production Ready ✅  

### Changelog v1.0.0
- ✨ Système de feedback automatique implémenté
- 📊 Dashboard analytics avec Chart.js
- 🤖 Modèles d'apprentissage automatique
- 📈 Métriques de performance en temps réel
- 🎯 Interface utilisateur optimisée
- 📱 Templates responsives avec Tailwind CSS

---

*Développé avec ❤️ pour améliorer les soins médicaux grâce à l'intelligence artificielle*

## Sécurité

- ⚠️ **IMPORTANT** : Ne jamais committer le fichier `.env` dans Git
- ✅ Le fichier `.gitignore` est configuré pour ignorer `.env`
- ✅ Utilisez `.env.example` comme template pour les nouveaux développeurs

## Structure des fichiers de configuration

```
AssistDoc/
├── .env                 # ❌ Ne pas committer (contient les vraies clés)
├── .env.example         # ✅ Template à committer
├── .gitignore          # ✅ Ignore .env
├── requirements.txt    # ✅ Dépendances Python
└── install.bat         # ✅ Script d'installation automatique
```

## Obtenir une clé API Gemini

1. Allez sur [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Créez une nouvelle clé API
3. Copiez la clé dans votre fichier `.env`

## Résolution des problèmes d'authentification

Si vous avez des problèmes de connexion :

1. Vérifiez que l'utilisateur existe dans la base de données
2. Vérifiez que `user_type = 'doctor'`
3. Vérifiez que le mot de passe est correct
4. Consultez les logs Django pour plus de détails
