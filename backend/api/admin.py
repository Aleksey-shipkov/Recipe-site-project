from django.contrib import admin
from food.models import Ingredients, IngredientsRecipe, Recipes, Tag, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'password', 'username', 'first_name', 'last_name')
    list_filter = ('username', 'email')


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


class IngRecipesInline(admin.TabularInline):
    model = IngredientsRecipe
    extra = 2


class RecipesAdmin(admin.ModelAdmin):
    inlines = (IngRecipesInline,)
    list_display = ('name', 'author', 'count_favorites')
    list_filter = ('author', 'name', 'tags')

    def count_favorites(self, obj):
        return obj.favorites.count()

    count_favorites.short_description = (
        'Количество добавлений рецепта в избранное'
    )


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(User, UserAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
