from django.db import models
from reviews.models.category import Category
from reviews.models.genre import Genre


class Title(models.Model):

    name = models.CharField(
        max_length=128,
        verbose_name='Название произведения',)

    year = models.IntegerField(
        verbose_name='Год произведения')

    description = models.TextField(
        verbose_name='Описание произведения',
        blank=True,
        null=True)

    genre = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='titles',
        verbose_name='Жанры')

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles',
        verbose_name='Категория')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['year']),
        ]
