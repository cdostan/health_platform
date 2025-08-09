from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=[('男','男'), ('女','女')], blank=True, null=True)
    # pass
    