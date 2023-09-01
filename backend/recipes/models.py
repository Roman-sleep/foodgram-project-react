from django.conf import settings
from django.db import models
from users.models import User
from django.core.validators import MinValueValidator


class Tag(models.Model):
    '''Модэль тэга.'''
    name = models.CharField(
        max_length=settings.MAX_LENGTH_255,
        unique=True,
        verbose_name='Название тэга'
    )
    color_code = models.CharField(
        max_length=settings.MAX_LENGTH_7,
        verbose_name='Цветовой код'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='slug'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    '''Модэль ингридиента.'''
    name = models.CharField(
        max_length=settings.MAX_LENGTH_255,
        verbose_name='Название ингридиента'
    )
    quantity = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Единици измерения'
    )
    unit = models.CharField(
        max_length=settings.MAX_LENGTH_50,
        verbose_name='Количество'
    )

    class Meta():
        verbose_name = 'Ингридиенты'
        verbose_name_plural = 'Ингридиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'quantity'],
                name='name_quantity_unique'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.quantity}'


class Recipe(models.Model):
    '''Модель рецепта.'''
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    title = models.CharField(
        max_length=settings.MAX_LENGTH_255,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipe_images',
        verbose_name='Изображение рецепта'
    )
    description = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингридиент'
    )
    favorites = models.ManyToManyField(
        User,
        through='FavoriteRecipe',
        related_name='Подписки на рецепт',
    )
    favorites_count = models.IntegerField(
        default=0,
        editable=False,
        verbose_name='Количество подписок',
    )
    ingredients_count = models.IntegerField(
        default=0,
        editable=False,
        verbose_name='Количество ингредиентов',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время готовки',
        validators=(MinValueValidator(
            1, message='Минимальное время приготовления 1 минута.'),
        )
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def update_favorites_count(self):
        self.favorites_count = self.favorites.count()
        self.save(update_fields=['favorites_count'])

    def update_ingredients_count(self):
        self.ingredients_count = self.ingredients.count()
        self.save(update_fields=['ingredients_count'])

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    '''Модэль ингридиентов в рецепте.'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент'
    )
    quantity = models.DecimalField(
        max_digits=settings.MAX_DIGITS_5,
        decimal_places=settings.DECIMAL_PLACES_2,
        verbose_name='Единици измерения'
    )
    unit = models.CharField(
        max_length=settings.MAX_LENGTH_50,
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return (
            f'{self.ingredient.name} :: {self.ingredient.quantity}'
            f' - {self.unit} '
        )


class Favorites(models.Model):
    """Модель избранного."""
    recipe = models.ForeignKey(
        verbose_name='Избранный рецепт',
        to=Recipe,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=User,
        on_delete=models.CASCADE
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='\n%(app_label)s_%(class)s recipe is favorite\n'
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"


class ShoppingList(models.Model):
    """Модель списка покупок."""
    recipe = models.ForeignKey(
        verbose_name='Рецепт в списке покупок',
        to=Recipe,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        verbose_name='Пользователь списка покупок',
        to=User,
        on_delete=models.CASCADE
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'

        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='\n%(app_label)s_%(class)s recipe is favorite\n'
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"
