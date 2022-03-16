from unicodedata import category
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User



class Source(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name



class UserIncome(models.Model):
    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.source.name} - {self.description}'

    
    class Meta:
        ordering = ['-date']

    
