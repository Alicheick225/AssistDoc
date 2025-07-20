# 🚀 Guide de Démarrage Rapide - Système IA AssistDoc

## ⚡ Installation Express (5 minutes)

### 1. Prérequis
```bash
# Vérifier Python
python --version  # Doit être 3.10+

# Vérifier Django
python -m django --version  # Doit être 5.2.4+
```

### 2. Activation de l'environnement
```bash
# Windows
cd d:\Google\google\AssistDoc
env\Scripts\activate

# Vérifier les dépendances
pip list | findstr "django\|google-generativeai"
```

### 3. Base de données
```bash
# Appliquer les migrations du système IA
python manage.py migrate

# Vérifier les nouvelles tables
python manage.py shell -c "from app.models import PrescriptionFeedback; print('✅ Tables IA créées')"
```

### 4. Lancement
```bash
# Démarrer le serveur
python manage.py runserver

# Accès rapide
# - Application: http://127.0.0.1:8000
# - Admin: http://127.0.0.1:8000/admin
# - Analytics: http://127.0.0.1:8000/admin/app/iaperformancemetrics/analytics/
```

---

## 🎯 Test Rapide du Système

### 1. Générer une prescription de test
1. Aller sur http://127.0.0.1:8000/dashboard
2. Sélectionner un patient
3. Créer une nouvelle consultation
4. Générer une prescription avec Gemini IA

### 2. Tester les fonctionnalités IA
```
✅ Valider → Feedback automatique créé
✏️ Modifier → Feedback "modifiée" créé  
❌ Annuler → Feedback "annulée" créé
🤖 Feedback IA → Formulaire complet
```

### 3. Vérifier les métriques
```bash
# Calculer les métriques
python manage.py calculate_ai_metrics

# Voir le résultat
# Admin → IA Performance Metrics → Analytics
```

---

## 📊 Points de Contrôle

### ✅ Checklist de Validation

- [ ] **Base de données** : Tables créées sans erreur
- [ ] **Modèles** : PrescriptionFeedback, AILearningData, IAPerformanceMetrics
- [ ] **Admin** : Interface accessible avec analytics
- [ ] **Vues** : URLs de feedback fonctionnelles
- [ ] **Templates** : Boutons d'action sur consultation_results.html
- [ ] **Commande** : calculate_ai_metrics s'exécute sans erreur
- [ ] **Graphiques** : Chart.js charge les analytics

### 🚨 Dépannage Express

**Erreur de migration :**
```bash
python manage.py makemigrations app --empty
# Éditer le fichier migration généré avec les modèles
python manage.py migrate
```

**Erreur Chart.js :**
```html
<!-- Vérifier dans analytics.html -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

**Erreur Gemini API :**
```python
# Vérifier dans settings.py
GEMINI_API_KEY = "your_api_key_here"
```

---

## 🎮 Commandes Utiles

```bash
# Système IA
python manage.py calculate_ai_metrics                    # Calcul métriques
python manage.py calculate_ai_metrics --date 2025-07-20  # Date spécifique

# Debug
python manage.py shell -c "from app.models import *; print(PrescriptionFeedback.objects.count())"
python manage.py showmigrations app                      # Voir migrations
python manage.py collectstatic                           # Assets statiques

# Base de données
python manage.py dbshell                                 # Accès direct DB
python manage.py dumpdata app.PrescriptionFeedback       # Export données
```

---

## 📞 Support Express

**Problème courant :**
- 🔧 **Serveur ne démarre pas** → Vérifier les migrations et la configuration
- 📊 **Pas de graphiques** → Vérifier Chart.js et les templates
- 🤖 **Pas de feedback** → Vérifier les URLs et les vues
- 📈 **Métriques vides** → Exécuter `calculate_ai_metrics`

**Liens rapides :**
- 📖 Documentation complète : `DOCUMENTATION_SYSTEME_IA.md`
- 🏥 Dashboard médecin : http://127.0.0.1:8000/dashboard
- ⚙️ Interface admin : http://127.0.0.1:8000/admin
- 📊 Analytics IA : http://127.0.0.1:8000/admin/app/iaperformancemetrics/analytics/

---

*Guide créé le 20/07/2025 - Version 1.0*
