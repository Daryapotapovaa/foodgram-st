from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(verbose_name='Почта', unique=True)
    first_name = models.CharField(verbose_name='Имя', max_length=150, blank=False)
    last_name = models.CharField(verbose_name='Фамилия', max_length=150, blank=False)
    avatar = models.ImageField(
        verbose_name='Аватарка',
        upload_to='users/images/',
        default=None,
        null=True, 
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
