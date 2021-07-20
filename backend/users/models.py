from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserAccountManager


class CustomUser(AbstractUser):
    email = models.EmailField('email', unique=True, max_length=254)
    username = models.CharField(
        'логин', max_length=150, blank=False, unique=True
    )
    first_name = models.CharField('имя', max_length=150, blank=False)
    last_name = models.CharField('фамилия', max_length=150, blank=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserAccountManager()

    class Meta:
        verbose_name_plural = 'пользователи'
        verbose_name = 'пользователь'
        ordering = ('username', )

    @property
    def is_admin(self):
        return self.is_superuser

    def __str__(self):
        return self.username
