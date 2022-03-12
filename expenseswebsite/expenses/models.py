from unicodedata import category
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User



class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    
    class Meta:
        verbose_name = ("Category")
        verbose_name_plural = ("Categories")



class Expense(models.Model):
    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.category.name} - {self.description}'

    
    class Meta:
        ordering = ['-date']

    
