@echo off
echo Installation des dépendances pour AssistDoc...

REM Activer l'environnement virtuel
call env\Scripts\activate.bat

REM Installer les dépendances
pip install -r requirements.txt

echo.
echo Installation terminée !
echo.
echo N'oubliez pas de :
echo 1. Copier .env.example vers .env
echo 2. Remplir vos vraies clés API dans le fichier .env
echo 3. Exécuter les migrations : python manage.py migrate
echo.
pause
