from django_filters import rest_framework as filters
from food.models import Recipes, Tag


class RecipesFilter(filters.FilterSet):
    author = filters.CharFilter(
        field_name='author__id',
        lookup_expr='contains'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug', to_field_name='slug',
        queryset=Tag.objects.all()
    )
    #tags = filters.CharFilter(
        #field_name='tags__slug',
        #lookup_expr='contains'
    #)

    class Meta:
        model = Recipes
        fields = ('author', 'tags')
