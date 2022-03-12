from django.contrib import admin
from .models import UserPreference
# Register your models here.

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'currency']