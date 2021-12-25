from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLES = (
        (USER, "user"),
        (MODERATOR, "moderator"),
        (ADMIN, "admin"),
    )

    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
        null=True
    )
    role = models.CharField(
        choices=ROLES,
        max_length=150,
        default='user'
    )
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения',
        max_length=150,
        blank=True,
        null=True
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['username']
