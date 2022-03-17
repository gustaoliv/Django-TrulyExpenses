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
    path('export_csv', views.export_csv, name='export_csv'),
]