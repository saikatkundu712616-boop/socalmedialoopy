from django.urls import path
from . import views

app_name = 'accounts'   

urlpatterns = [
     path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),


    path('discover/', views.discover_view, name='discover'),

    # profile
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),

    # ajax
    path('follow/<str:username>/', views.follow_toggle, name='follow_toggle'),
]