from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
# Create your views here.


@login_required(login_url='login')
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 6)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
    }
    return render(request, 'expenses/index.html', context)


def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }

    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        
        if not amount:
            messages.error(request, 'Amount is required')

        description = request.POST['description']
        if not description:
            messages.error(request, 'Description is required')

        category = Category.objects.get(id=int(request.POST['category']))
        
        
        if amount and description and category:
            if request.POST['expense_date']:
                date = request.POST['expense_date']
                expense = Expense.objects.create(amount=amount, description=description, category=category, date=date, owner=request.user)
            else:
                expense = Expense.objects.create(amount=amount, description=description, category=category, owner=request.user)

            expense.save()
            messages.success(request, 'Expense saved successfully')
            return redirect('expenses')

        return render(request, 'expenses/add_expense.html', context)



def edit_expense(request, id):

    expense = Expense.objects.get(id=id)
    categories = Category.objects.all()
    print(expense.date)
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories,
    }
    
    if request.method == 'GET':
        return render(request, 'expenses/edit_expense.html', context)

    else:
        amount = request.POST['amount']
        
        if not amount:
            messages.error(request, 'Amount is required')
            

        description = request.POST['description']
        if not description:
            messages.error(request, 'Description is required')

        category = Category.objects.get(id=int(request.POST['category']))
        
        
        if amount and description and category:
            expense.amount=amount
            expense.description=description
            expense.category=category
            if request.POST['expense_date']:
                date = request.POST['expense_date']
                expense.date = date
                
            expense.save()

            messages.success(request, 'Expense updated successfully')
            return redirect('expenses')

        return render(request, 'expenses/edit_expense.html', context)


        
def delete_expense(request, id):
    expense = Expense.objects.get(id=id)
    expense.delete()
    messages.success(request, 'Expense deleted successfully')
    return redirect('expenses')



def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')

        expenses = Expense.objects.filter(
            amount__istartswith=search_str,
            owner = request.user,  
        ) | Expense.objects.filter(
            date__istartswith=search_str,
            owner = request.user,  
        ) | Expense.objects.filter(
            description__icontains=search_str,
            owner = request.user,  
        ) | Expense.objects.filter(
            category__name__icontains=search_str,
            owner = request.user,  
        ) 

        
        data = expenses.values()
        for exp in data:
            exp['category'] = str(Category.objects.get(id=exp['category_id']))
        

        return JsonResponse(list(data), safe=False)