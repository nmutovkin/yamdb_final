from django.db import models


class Category(models.Model):

    name = models.CharField(
        max_length=256,
        verbose_name='Название категории')

    slug = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name='Уникальное имя категории')

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name
