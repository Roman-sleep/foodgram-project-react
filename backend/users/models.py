from django.db import models
from django.db.models import F, Q, UniqueConstraint


class User(models.Model):
    """ Модель пользователя. """
    first_name = models.CharField(
        max_length=255,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Почта'
    )
    username = models.CharField(
        max_length=255,
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
        verbose_name='Автор'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
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

    def __str__(self) -> str:
        return f"{self.user} подписан на {self.author}"
