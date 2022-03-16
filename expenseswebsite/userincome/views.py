from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages


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
    sources = Source.objects.all()
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
                expense = UserIncome.objects.create(amount=amount, description=description, source=source, date=date, owner=request.user)
            else:
                expense = UserIncome.objects.create(amount=amount, description=description, source=source, owner=request.user)

            expense.save()
            messages.success(request, 'Record saved successfully')
            return redirect('incomes')

        return render(request, 'incomes/add_income.html', context)


