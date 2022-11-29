from django_filters import rest_framework as filters

from food.models import Recipes, Tag


class RecipesFilter(filters.FilterSet):
    is_in_shopping_cart = filters.CharFilter(method="get_is_in_shopping_cart")
    is_favorited = filters.CharFilter(method="get_is_favorited")
    author = filters.CharFilter(
        field_name="author__id", lookup_expr="contains"
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipes
        fields = ("author", "tags")

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value == "1":
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    def get_is_favorited(self, queryset, name, value):
        if value == "1":
            return queryset.filter(favorites__user=self.request.user)
        return queryset
