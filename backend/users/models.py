from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserAccountManager


class CustomUser(AbstractUser):
    email = models.EmailField('email', unique=True)
    username = models.CharField(
        'логин', max_length=30, blank=True, unique=True
    )
    first_name = models.CharField('имя', max_length=50, blank=True)
    last_name = models.CharField('фамилия', max_length=50, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserAccountManager()

    @property
    def is_admin(self):
        return self.is_superuser

    def __str__(self):
        return self.email
