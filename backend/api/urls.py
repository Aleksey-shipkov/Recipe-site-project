from django.urls import include, path

from rest_framework import routers

from api.views import (FavoriteView, IngredientsViewSet, RecipesViewSet,
                       ShoppingCartView, SubscriptionsListView,
                       SubscriptionsView, TagViewSet, UserViewSet)

router = routers.DefaultRouter()
router.register(r'^users', UserViewSet)
router.register(r'^recipes', RecipesViewSet, basename='recipes')
router.register(r'^tags', TagViewSet)
router.register(r'^ingredients', IngredientsViewSet)

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscriptionsListView.as_view()),
    path('users/<int:id>/subscribe/', SubscriptionsView.as_view()),
    path('recipes/<int:id>/favorite/', FavoriteView.as_view()),
    path('recipes/<int:id>/shopping_cart/', ShoppingCartView.as_view()),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
