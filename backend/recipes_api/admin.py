from django.contrib import admin

from .models import Ingredient, Recipe, Tag, RecipeIngredient
from users.models import CustomUser


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


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
    list_display = ('name', 'text', 'cooking_time')
    list_filter = ('name', 'tag',)
    empty_value_display = '-пусто-'
    inlines = [RecipeIngredientInline, ]


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email',)
    list_filter = ('username', 'email',)
    empty_value_display = '-пусто-'


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
