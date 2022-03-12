import re
from django.shortcuts import render
import os
import json
from django.conf import settings
from .models import UserPreference
from django.contrib import messages


def index(request):
    exists = UserPreference.objects.filter(user=request.user).exists()
    user_preferences = None


    
    

    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')
    # import pdb
    # pdb.set_trace()
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            currency_data.append({'name': k, 'value': v})


    context = {
        'currencies': currency_data,
    }
    
    if exists:
        user_preferences = UserPreference.objects.get(user=request.user)
        context['user_currency'] = user_preferences.currency

    if request.method == 'GET':
        
        return render(request, 'preferences/index.html', context)

    else:
        currency = request.POST['currency']
        if exists:
            user_preferences.currency = currency
            user_preferences.save()
            context['user_currency'] = user_preferences.currency
        else:
            UserPreference.objects.create(user=request.user, currency=currency)
        
        messages.success(request, 'Changes saved')

        return render(request, 'preferences/index.html', context)