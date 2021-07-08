from django.contrib import admin

from .models import Ingredient, Recipe, Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagAdmin)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name', 'tag',)
    empty_value_display = '-пусто-'


admin.site.register(Recipe)
