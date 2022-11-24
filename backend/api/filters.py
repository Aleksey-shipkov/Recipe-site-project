from django_filters import rest_framework as filters
from food.models import Recipes


class RecipesFilter(filters.FilterSet):
    author = filters.CharFilter(
        field_name='author__id',
        lookup_expr='contains'
    )
    tags = filters.CharFilter(
        field_name='tags__slug',
        lookup_expr='contains'
    )

    class Meta:
        model = Recipes
        fields = ('author', 'tags')
