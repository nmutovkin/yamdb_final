from django.db import models
from reviews.models.review import Review
from reviews.models.user import User


class Comment(models.Model):

    text = models.TextField(
        verbose_name='Текст комментария')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария')

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания комментария')

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв')

    def __str__(self):
        return self.text[:20]

    class Meta:
        ordering = ['-pub_date']
