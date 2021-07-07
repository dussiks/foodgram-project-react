from django.db import models

# from users.models import FoodUser


class Tag(models.Model):
    name = models.CharField('тег', max_length=50, unique=True, blank=False)
    slug = models.SlugField(max_length=20, unique=True)
    color = models.CharField(
        'цвет', unique=True, max_length=7, default='#49B64E'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'теги'
        ordering = ('name',)


class Ingredient(models.Model):
    name = models.CharField('ингредиент', max_length=40, blank=False)
    measurement_unit = models.CharField('ЕИ', max_length=20, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'ингредиенты'
        ordering = ('name',)


class Recipe(models.Model):
    # author = models.ForeignKey(FoodUser, on_delete=models.CASCADE, null=False)
    name = models.CharField('рецепт', max_length=40, blank=False)
    image = models.ImageField(
        'рисунок', upload_to='api/', null=False, blank=False
    )
    text = models.TextField('описание', blank=False)
    cooking_time = models.PositiveSmallIntegerField('время готовки, мин',
                                                    blank=False)
    tag = models.ManyToManyField(Tag, related_name='tags', null=False)
    ingredient = models.ManyToManyField(Ingredient,
                                        through='RecipeIngredient')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'рецепты'
        ordering = ('name',)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, blank=False)
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE, blank=False)
    amount = models.PositiveSmallIntegerField(blank=False)
