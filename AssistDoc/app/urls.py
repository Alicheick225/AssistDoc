from django.urls import path
from .views import (
    consultation, patient_detail, dashboard, index, login_page, symptome, 
    traiter_consultation, supprimer_consultation, valider_consultation, 
    modifier_prescription, donner_feedback, annuler_prescription
)

urlpatterns = [
    path('', index, name='index'),
    path('login/', login_page, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('consultation/', consultation, name='consultation'),
    path('symptome/<str:patient_social_security_number>/', symptome, name='symptome'),
    path('traiter-consultation/', traiter_consultation, name='traiter_consultation'),
    path('valider-consultation/<int:consultation_id>/', valider_consultation, name='valider_consultation'),
    path('modifier-prescription/<int:consultation_id>/', modifier_prescription, name='modifier_prescription'),
    path('supprimer-consultation/<int:consultation_id>/', supprimer_consultation, name='supprimer_consultation'),
    path('donner-feedback/<int:consultation_id>/', donner_feedback, name='donner_feedback'),
    path('annuler-prescription/<int:consultation_id>/', annuler_prescription, name='annuler_prescription'),
    path("patients/<int:pk>/", patient_detail, name="patient_detail"),
]
