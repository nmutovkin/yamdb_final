from django.db import models
from django.core.exceptions import ValidationError
from reviews.models.title import Title
from reviews.models.user import User


def check_score(value):
    if not (1 <= value <= 10):
        raise ValidationError(
            f'{value} is not between 1 and 10'
        )


class Review(models.Model):

    text = models.TextField(
        verbose_name='Текст отзыва')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва')

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создание отзыва')

    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[check_score])

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение')

    def __str__(self):
        return self.text[:20]

    class Meta:
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='only_one_author'
            )
        ]
