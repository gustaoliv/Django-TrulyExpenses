from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('', views.index, name='incomes'),
    path('add-income', views.add_income, name='add-income'),
    path('edit-income/<int:id>', views.edit_income, name='edit-income'),
    path('delete_income/<int:id>', views.delete_income, name='delete_income'),
    path('search_incomes', csrf_exempt(views.search_incomes), name='search_incomes'),
    path('add_source/<int:opt>/<int:pk>', views.add_source, name='add_source'),
]