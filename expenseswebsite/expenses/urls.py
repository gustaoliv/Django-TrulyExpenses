from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('', views.index, name='expenses'),
    path('add-expense', views.add_expense, name='add-expense'),
    path('edit-expense/<int:id>', views.edit_expense, name='edit-expense'),
    path('delete_expense/<int:id>', views.delete_expense, name='delete_expense'),
    path('search_expenses', csrf_exempt(views.search_expenses), name='search_expenses'),
    path('expense_category_summary', views.expense_category_summary, name='expense_category_summary'), 
    path('stats', views.status_view, name='stats'),
    path('expense_income_charts_summary', views.expense_income_charts_summary, name='expense_income_charts_summary'), 
    path('expeses_incomes_charts', views.expense_income_charts_view, name='expeses_incomes_charts'),
    path('export_csv', views.export_csv, name='export_csv'),
    path('export_excel', views.export_excel, name='export_excel'),
    path('export_pdf', views.export_pdf, name='export_pdf'),
    path('add_category/<int:opt>/<int:pk>', views.add_category, name='add_category'),
]