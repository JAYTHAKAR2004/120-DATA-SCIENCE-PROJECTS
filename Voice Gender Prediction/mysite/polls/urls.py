from django.urls import path
from .views import Voice

urlpatterns = [
    path('Voice/', Voice, name='voice_reveal'),
    ]