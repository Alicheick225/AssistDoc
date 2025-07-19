from django.urls import path
from .views import consultation, patient_detail, dashboard, index, login_page, symptome

urlpatterns = [
    path('', index, name='index'),
    path('login/', login_page, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('consultation/', consultation, name='consultation'),
    path('symptome/<int:patient_social_security_number>/', symptome, name='symptome'),
    path("patients/<int:pk>/", patient_detail, name="patient_detail"),
]
