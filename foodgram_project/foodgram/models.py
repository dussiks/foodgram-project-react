from django.db import models


class Tag(models.Model):
    name = models.CharField('тег', max_length=50, unique=True, blank=False)
    slug = models.SlugField(max_length=20, unique=True)
    hex_code = models.CharField(
        'hex-код тега', unique=True, max_length=7, default='#49B64E'
    )

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    name = models.CharField('ингредиент', max_length=40)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField('рецепт', max_length=40)
    image = models.ImageField('рисунок')
    description = models.TextField('описание')
    time = models.PositiveSmallIntegerField('время готовки, мин')
    tag = models.ManyToManyField(Tag)

    def __str__(self):
        return self.name


