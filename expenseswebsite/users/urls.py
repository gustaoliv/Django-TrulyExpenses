from django.urls import path
from . import views 

urlpatterns = [
    path('', views.profile_settings, name='profile-settings'),
]