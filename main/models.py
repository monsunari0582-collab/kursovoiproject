from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
  ROLES = [
    ('student', 'Ученик'),
    ('coach', 'Тренер'),
    ('admin', 'Администратор'),
  ]

  role = models.CharField(max_length=20, choices=ROLES, default='student')
# Create your models here.
