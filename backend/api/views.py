from api.filters import RecipesFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientsRecipeSerializer,
                             IngredientsSerializer, RecipesCreateSerializer,
                             RecipesSerializer, ShoppingCartSerializer,
                             SubscriptionsListSerializer,
                             SubscriptionsSerializer, TagSerializer)
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from food.models import (Favorite, Ingredients, IngredientsRecipe, Recipes,
                         ShoppingCart, Subscriptions, Tag, User)
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitPageNumberPagination

    @action(
        detail=False, methods=['GET'], permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class RecipesViewSet(viewsets.ModelViewSet):
    serializer_class = RecipesSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipesSerializer
        else:
            return RecipesCreateSerializer

    def get_queryset(self):
        queryset = Recipes.objects.all()
        favorited = self.request.query_params.get('is_favorited')
        shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        if favorited == '1':
            queryset = Recipes.objects.filter(
                favorites__user=self.request.user
            )
        if shopping_cart == '1':
            queryset = Recipes.objects.filter(
                shopping_cart__user=self.request.user
            )
        return queryset

    @action(
        detail=False, methods=['GET'], permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        shop_cart = IngredientsRecipe.objects.filter(
            recipe__shopping_cart__user=self.request.user.id
        )
        shop_cart_sum = (
            shop_cart.values('ingredient').annotate(sum_ing=Sum('amount'))
        )
        response = HttpResponse(content_type='text/plain; charset=UTF-8')
        response['Content-Disposition'] = (
            'attachment; filename="shopping-cart.txt"'
        )

        ing_list = []

        for ing, sum_ing in shop_cart_sum.values_list('ingredient', 'sum_ing'):
            ingr = Ingredients.objects.get(id=ing)
            ing_list.append(
                f'{ingr.name} ({ingr.measurement_unit}) - {sum_ing}\n'
            )

        response.writelines(ing_list)
        return response


class SubscriptionsListView(ListAPIView):
    serializer_class = SubscriptionsListSerializer
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        new_queryset = User.objects.filter(following__user=user)
        return new_queryset


class SubscriptionsView(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = Subscriptions.objects.all()
    serializer_class = SubscriptionsSerializer

    def perform_create(self, serializer):
        serializer.save(
            author_id=self.kwargs['id'], user_id=self.request.user.id
        )

    def destroy(self, request, *args, **kwargs):
        author_id = self.kwargs['id']
        author = User.objects.get(id=author_id)
        user = self.request.user
        if not Subscriptions.objects.filter(user=user, author=author).exists():
            return Response(
                'Вы не подписывались на этого автора.',
                status=status.HTTP_400_BAD_REQUEST)
        Subscriptions.objects.filter(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    permission_classes = (AllowAny,)


class IngredientsRecipeViewSet(viewsets.ModelViewSet):
    queryset = IngredientsRecipe.objects.all()
    serializer_class = IngredientsRecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class FavoriteView(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def perform_create(self, serializer):
        serializer.save(
            recipe_id=self.kwargs['id'], user_id=self.request.user.id
        )

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs['id']
        recipe = Recipes.objects.get(id=recipe_id)
        user = self.request.user
        if not Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                'Рецепт отсутствует в избранном',
                status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartView(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer

    def perform_create(self, serializer):
        serializer.save(
            recipe_id=self.kwargs['id'], user_id=self.request.user.id
        )

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs['id']
        recipe = Recipes.objects.get(id=recipe_id)
        user = self.request.user
        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                'Рецепт отсутствует в списке покупок',
                status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
