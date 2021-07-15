from django.db import models
from django.core.validators import RegexValidator

from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField('тег', max_length=50, unique=True, blank=False)
    slug = models.SlugField(max_length=20, unique=True)
    color = models.CharField(
        'цвет',
        unique=True,
        max_length=7,
        default='#49B64E',
        validators=[
            RegexValidator(regex=r'#[a-fA-F0-9]{6}$',
                           message='Color should be in hex-field form.')
        ]
    )

    class Meta:
        verbose_name_plural = 'теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('ингредиент', max_length=40, blank=False)
    measurement_unit = models.CharField('ЕИ', max_length=20, blank=False)

    class Meta:
        verbose_name_plural = 'ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=False, blank=False
    )
    name = models.CharField('рецепт', max_length=40,
                            blank=False, db_index=True)
    image = models.ImageField(
        'рисунок', upload_to='recipes_api/', null=False, blank=False
    )
    text = models.TextField('описание', blank=False)
    cooking_time = models.PositiveSmallIntegerField('время готовки, мин',
                                                    blank=False)
    tag = models.ManyToManyField(Tag, related_name='tags')
    ingredient = models.ManyToManyField(Ingredient,
                                        through='RecipeIngredient')

    class Meta:
        verbose_name_plural = 'рецепты'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, blank=False)
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE, blank=False)
    amount = models.PositiveSmallIntegerField(blank=False)


class Follow(models.Model):
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                 related_name='followers')
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                  related_name='followings')

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'], name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.follower} подписан на {self.following}'
