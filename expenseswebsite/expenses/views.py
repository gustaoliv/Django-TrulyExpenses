from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreference
import datetime
import csv
import xlwt
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum
from .forms import CategoryForm
from userincome.models import UserIncome
# Create your views here.


@login_required(login_url='login')
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 6)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        currency = ""
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency,
    }
    return render(request, 'expenses/index.html', context)


def add_expense(request):
    categories = Category.objects.filter(owner=request.user)
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
    categories = Category.objects.filter(owner=request.user)
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



def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_category(expense):
        return expense.category
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y.name] = get_expense_category_amount(y)


    amount_month = {}
    for exp in expenses:
        month = exp.date.strftime('%b')
        amount = exp.amount
        
        if month in amount_month.keys():
            amount_month[month] += amount
        else:
            amount_month[month] = amount

    return JsonResponse({'expense_category_data': finalrep, 'amount_month': amount_month}, safe=False)



def status_view(request):
    return render(request, 'expenses/stats.html')


def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + str(datetime.datetime.now()) + '.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])
    expenses = Expense.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])

    return response


def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + str(datetime.datetime.now()) + '.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Amount', 'Description', 'Category', 'Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Expense.objects.filter(owner=request.user).values_list('amount', 'description', 'category', 'date')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if isinstance(row[col_num], int):
                ws.write(row_num, col_num, str(Category.objects.get(id=row[col_num])), font_style)
            else:
                ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)

    return response


def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename=Expenses' + str(datetime.datetime.now()) + '.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    expenses = Expense.objects.filter(owner=request.user)

    sum = expenses.aggregate(Sum('amount'))

    html_string = render_to_string('expenses/pdf-output.html', {'expenses': expenses, 'total': sum['amount__sum']})
    html = HTML(string=html_string)

    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output.seek(0)
        response.write(output.read())

    return response



def add_category(request, opt, pk):
    form = CategoryForm(request.POST)

    if form.is_valid():
        register = form.save(commit=False)
        register.owner = request.user
        register.save()
        messages.success(request, 'Category created successfully')

    if opt == 1:
        return redirect('add-expense')
    else:
        return redirect('edit-expense', pk)




def expense_income_charts_view(request):
    return render(request, 'expenses/expense_income_charts_view.html')


def expense_income_charts_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    expenses_list = Expense.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)

    incomes_list = UserIncome.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)

    incomes = {}
    expenses = {}
    
    for exp in expenses_list:
        month = exp.date.strftime('%b')
        amount = exp.amount
        
        if month in expenses.keys():
            expenses[month] += amount
        else:
            expenses[month] = amount


    for inc in incomes_list:
        month = inc.date.strftime('%b')
        amount = inc.amount
        
        if month in incomes.keys():
            incomes[month] += amount
        else:
            incomes[month] = amount


    for month in incomes:
        if month not in expenses.keys():
            expenses[month] = 0
    
    for month in expenses:
        if month not in incomes.keys():
            incomes[month] = 0

    result_incomes = {}
    for key in sorted(incomes.keys()):
        result_incomes[key] = incomes[key]

    result_expenses = {}
    for key in sorted(expenses.keys()):
        result_expenses[key] = expenses[key]


    
    return JsonResponse({'incomes': result_incomes, 'expenses': result_expenses}, safe=False)