from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('api/generer-prescription/', views.generer_prescription, name='generer_prescription'),
]