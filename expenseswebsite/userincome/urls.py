from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('', views.index, name='incomes'),
    path('add-income', views.add_income, name='add-income'),
    # path('edit-expense/<int:id>', views.edit_expense, name='edit-expense'),
    # path('delete_expense/<int:id>', views.delete_expense, name='delete_expense'),
    # path('search_expenses', csrf_exempt(views.search_expenses), name='search_expenses'),
]