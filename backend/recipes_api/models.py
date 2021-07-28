from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField('тег', max_length=200, unique=True)
    slug = models.SlugField('слаг', max_length=200, unique=True)
    color = models.CharField(
        'цвет',
        max_length=7,
        default='#49B64E',
        validators=[
            RegexValidator(regex=r'#[a-fA-F0-9]{6}$',
                           message='Color should be in hex-field form.')
        ]
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('ингредиент', max_length=200, db_index=True)
    measurement_unit = models.CharField('ЕИ', max_length=200)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               null=False, verbose_name='автор',
                               related_name='recipes')
    name = models.CharField('рецепт', max_length=40, db_index=True)
    image = models.ImageField('рисунок', upload_to='recipes_api/', null=False)
    text = models.TextField('описание')
    cooking_time = models.IntegerField(
        verbose_name='время готовки, мин',
        validators=[MinValueValidator(
            1,
            message='Введите целое число больше 0 для времени готовки.'
        )],
    )
    tags = models.ManyToManyField(Tag, related_name='recipes',
                                  verbose_name='теги')
    ingredients = models.ManyToManyField(Ingredient,
                                         verbose_name='ингредиенты',
                                         through='RecipeIngredient')

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('-id',)

    def __str__(self):
        return self.name

    def favorites_count(self):
        return str(self.favorites.all().count())
    favorites_count.short_description = 'В избранном:'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_ingredients',
                               verbose_name='рецепт')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name='ингредиент')
    amount = models.IntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(
            1,
            message='Введите целое число больше 0 для количества.'
        )],
    )

    class Meta:
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = 'Количества ингредиентов в рецептах'
        ordering = ('-id',)


class Follow(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='followers',
                             verbose_name='подписчик')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               related_name='followings',
                               verbose_name='автор')

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='favorites',
                             verbose_name='пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favorites',
                               verbose_name='рецепт')

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в избранном {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='shopping_carts',
                             verbose_name='пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='shopping_carts',
                               verbose_name='рецепт')

    class Meta:
        verbose_name = 'рецепт в корзине'
        verbose_name_plural = 'рецепты в корзине'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shop'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в корзине {self.user}'
