from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
import json
from django.http import JsonResponse


@login_required(login_url='login')
def index(request):
    incomes = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(incomes, 6)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'incomes': incomes,
        'page_obj': page_obj,
        'currency': currency,
    }
    return render(request, 'incomes/index.html', context)


def add_income(request):
    sources = Source.objects.filter(owner=request.user)
    context = {
        'sources': sources,
        'values': request.POST
    }

    if request.method == 'GET':
        return render(request, 'incomes/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        
        if not amount:
            messages.error(request, 'Amount is required')

        description = request.POST['description']
        if not description:
            messages.error(request, 'Description is required')

        source = Source.objects.get(id=int(request.POST['source']))
        
        
        if amount and description and source:
            if request.POST['income_date']:
                date = request.POST['income_date']
                income = UserIncome.objects.create(amount=amount, description=description, source=source, date=date, owner=request.user)
            else:
                income = UserIncome.objects.create(amount=amount, description=description, source=source, owner=request.user)

            income.save()
            messages.success(request, 'Record saved successfully')
            return redirect('incomes')

        return render(request, 'incomes/add_income.html', context)


def edit_income(request, id):

    income = UserIncome.objects.get(id=id)
    sources = Source.objects.filter(owner=request.user)
    context = {
        'income': income,
        'values': income,
        'sources': sources,
    }
    
    if request.method == 'GET':
        return render(request, 'incomes/edit_income.html', context)

    else:
        amount = request.POST['amount']
        
        if not amount:
            messages.error(request, 'Amount is required')
            

        description = request.POST['description']
        if not description:
            messages.error(request, 'Description is required')

        source = Source.objects.get(id=int(request.POST['source']))
        
        
        if amount and description and source:
            income.amount=amount
            income.description=description
            income.category=source
            if request.POST['income_date']:
                date = request.POST['income_date']
                income.date = date
                
            income.save()

            messages.success(request, 'Income updated successfully')
            return redirect('incomes')

        return render(request, 'income/edit_income.html', context)



def delete_income(request, id):
    income = UserIncome.objects.get(id=id)
    income.delete()
    messages.success(request, 'Income deleted successfully')
    return redirect('incomes')



def search_incomes(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')

        incomes = UserIncome.objects.filter(
            amount__istartswith=search_str,
            owner = request.user,  
        ) | UserIncome.objects.filter(
            date__istartswith=search_str,
            owner = request.user,  
        ) | UserIncome.objects.filter(
            description__icontains=search_str,
            owner = request.user,  
        ) | UserIncome.objects.filter(
            source__name__icontains=search_str,
            owner = request.user,  
        ) 

        
        data = incomes.values()
        for exp in data:
            exp['source'] = str(Source.objects.get(id=exp['source_id']))
        

        return JsonResponse(list(data), safe=False)