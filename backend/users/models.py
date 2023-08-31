from django.conf import settings
from django.db import models
from django.db.models import F, Q, UniqueConstraint


class User(models.Model):
    """ Модель пользователя. """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    first_name = models.CharField(
        max_length=settings.MAX_LENGTH_255,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=settings.MAX_LENGTH_255,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Почта'
    )
    username = models.CharField(
        max_length=settings.MAX_LENGTH_255,
        unique=True,
        verbose_name='Никнэйм'
    )

    class Meta:
        verbose_name = 'Пользователь'

    def __str__(self):
        return self.username


class Follow(models.Model):

    """ Модель подписки на автора. """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='follower'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='following'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='no_self_follow'
            )
        ]
        verbose_name = 'Подписка'
        ordering = ['-id']

    def str(self) -> str:
        return f"{self.user} подписан на {self.author}"
