"""Defines URL patterns for user resources of humanspace app"""

from django.urls import path, include
from . import views

app_name = "users"
urlpatterns = [
        # Default auth urls.
        path('', include('django.contrib.auth.urls')),
        # Registration 
        path('register/', views.register, name='register'),
        
        # Auth
        path('auth/login/', views.twitter_login, name='twitter_login'),
        path('auth/login/callback/', views.twitter_callback, name='twitter_callback'),
        ]
