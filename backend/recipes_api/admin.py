import models
from django.contrib import admin


class RecipeIngredientInline(admin.TabularInline):
    model = models.RecipeIngredient
    fields = ('ingredient', 'amount')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'text', 'cooking_time', 'favorites_count')
    list_filter = ('author', 'name', 'tags',)
    empty_value_display = '-пусто-'
    inlines = [RecipeIngredientInline, ]


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    empty_value_display = '-пусто-'


admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Follow, FollowAdmin)
admin.site.register(models.Favorite, FavoriteAdmin)
admin.site.register(models.ShoppingCart, ShoppingCartAdmin)
admin.site.register(models.RecipeIngredient)
