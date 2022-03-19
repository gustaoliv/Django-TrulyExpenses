from django.forms import ModelForm
from .models import Category


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name',]