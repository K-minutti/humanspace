"""Defines URL patterns for humanspace app"""

from django.urls import path
from . import views

app_name = "humanspace_app"
urlpatterns = [
        # Root page
        path('', views.index, name='index'),
        # Home page
        path('home/', views.home, name='home'),

        # Auth
        path('user/logout/', views.app_logout, name='app_logout'),

        # Topics
        path('topics/', views.topics, name='topics'),
        path('topics/<int:topic_id>/', views.topic, name='topic'),
        path('new_topic/', views.new_topic, name='new_topic'),

        # Entries
        path('new_entry/<int:topic_id>/', views.new_entry, name='new_entry'),
        path('edit_entry/<int:entry_id>/', views.edit_entry, name='edit_entry'),

        #Bookmarks 
        path('bookmarks/', views.bookmarks, name='bookmarks'),
        ]

