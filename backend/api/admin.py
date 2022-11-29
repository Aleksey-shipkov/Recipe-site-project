from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from food.models import (
    Favorite,
    Ingredients,
    IngredientsRecipe,
    Recipes,
    ShoppingCart,
    Subscriptions,
    Tag,
    User,
)


class UserCustomAdmin(UserAdmin):
    list_display = ("email", "username", "first_name", "last_name", "password")
    search_fields = ("username", "email")


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    search_fields = ("user__username", "author__username")


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")


class IngredientsRecipeAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "recipe", "amount")
    search_fields = ("ingredient__name", "recipe__name")


class IngRecipesInline(admin.TabularInline):
    model = IngredientsRecipe
    extra = 2


class RecipesAdmin(admin.ModelAdmin):
    inlines = (IngRecipesInline,)
    list_display = ("name", "author", "count_favorites")
    list_filter = ("tags",)
    search_fields = ("author", "name")

    def count_favorites(self, obj):
        return obj.favorites.count()

    count_favorites.short_description = (
        "Количество добавлений рецепта в избранное"
    )


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)


admin.site.register(User, UserCustomAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Subscriptions, SubscriptionsAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(IngredientsRecipe, IngredientsRecipeAdmin)
