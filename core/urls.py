# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/count/', views.unread_notifications_count,
         name='notifications_count'),
    path('search/', views.search_view, name='search'),
    path('contact/', views.contact_view, name='contact'),
]