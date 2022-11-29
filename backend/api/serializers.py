import base64

from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.db import transaction
from django.shortcuts import get_object_or_404

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator

from backend.settings import MIN_TIME, MIN_AMOUNT
from food.models import (
    Favorite,
    Ingredients,
    IngredientsRecipe,
    Recipes,
    ShoppingCart,
    Subscriptions,
    Tag,
    User
)


class RecipesUserSerializer(serializers.ModelSerializer):
    """Сокращенное представление информации о рецептах."""

    class Meta:
        model = Recipes
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionsListSerializer(serializers.ModelSerializer):
    """Сериалайзер для списка подписок пользователя."""

    recipes = serializers.SerializerMethodField(method_name="get_recipes")
    recipes_count = serializers.SerializerMethodField(
        method_name="get_recipes_count"
    )
    is_subscribed = serializers.SerializerMethodField(
        method_name="get_is_subscribed"
    )

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        context = self.context
        request = context.get("request")
        if request.user.is_authenticated:
            return Subscriptions.objects.filter(
                user=request.user, author=obj.id
            ).exists()
        return False

    def get_recipes(self, obj):
        request = self.context["request"]
        limit = request.GET.get("recipes_limit")
        queryset = obj.recipes.all()
        if limit:
            queryset = queryset[: int(limit)]
        return RecipesUserSerializer(queryset, many=True).data


class SubscriptionsIdSerializer(serializers.ModelSerializer):
    """Сериализатор для информации о пользователе на которого подписались."""

    recipes = RecipesUserSerializer(many=True)
    recipes_count = serializers.SerializerMethodField(
        method_name="get_recipes_count"
    )
    is_subscribed = serializers.SerializerMethodField(
        method_name="get_is_subscribed"
    )

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "recipes",
            "is_subscribed",
            "recipes_count",
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        current_user = self.context["user"]
        return Subscriptions.objects.filter(
            user=current_user, author=obj.id
        ).exists()


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки и отписки от пользователя."""

    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    author = serializers.SerializerMethodField(method_name="get_author")

    class Meta:
        model = Subscriptions
        fields = ("user", "author")

    def get_author(self, obj):
        author_id = self.instance.author_id
        return author_id

    def validate(self, data):
        my_view = self.context["view"]
        author_id = my_view.kwargs.get("id")
        author = get_object_or_404(User, id=author_id)
        user = self.context["request"].user
        subscription = Subscriptions.objects.filter(user=user, author=author)
        if subscription.exists():
            raise serializers.ValidationError("Уже подписаны на этого автора")
        if user == author:
            raise serializers.ValidationError(
                "Подписаться на самого себя не возможно"
            )
        if (
            self.context["request"].method == "DELETE"
            and not subscription.exists()
        ):
            return Response(
                "Вы не подписывались на этого автора.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def to_representation(self, instance):
        author_id = instance.author.id
        author = get_object_or_404(User, id=author_id)
        user = self.instance.user
        serializer = SubscriptionsIdSerializer(author, context={"user": user})
        return serializer.data


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class UserSerializer(UserSerializer):
    """Сериализатор для вывода информации пользователях."""

    is_subscribed = serializers.SerializerMethodField(
        method_name="get_is_subscribed"
    )

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        context = self.context
        user = context["request"].user
        if user.is_authenticated:
            author = obj.id
            return Subscriptions.objects.filter(
                user=user, author=author
            ).exists()
        return False


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода списка или отдельного ингредиента."""

    class Meta:
        model = Ingredients
        fields = ("id", "name", "measurement_unit")


class IngredientsRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели количества ингредиентов в каждом рецепте."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientsRecipe
        fields = ("id", "name", "measurement_unit", "amount")
        read_only_fields = ("name", "measurement_unit")


class IngredientsCreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/удаления
    записи о количестве ингридиентов в рецепте."""

    id = serializers.IntegerField(required="True")
    amount = serializers.IntegerField(
        required="True", validators=(MinValueValidator(MIN_AMOUNT),)
    )

    class Meta:
        model = IngredientsRecipe
        read_only_fields = ("recipe", "ingredient")
        fields = ("id", "amount")


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для внесения/исключения ингредиентов из списка покупок."""

    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    recipe = serializers.SerializerMethodField(method_name="get_recipe")

    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")

    def get_recipe(self, obj):
        recipe_id = self.instance.id
        return recipe_id

    def validate(self, data):
        my_view = self.context["view"]
        recipe_id = my_view.kwargs.get("id")
        current_user = self.context["request"].user
        recipe = get_object_or_404(Recipes, id=recipe_id)
        if ShoppingCart.objects.filter(
            user=current_user, recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                "Вы уже добавили этот рецепт список покупок."
            )
        return data

    def to_representation(self, instance):
        recipe_id = instance.recipe.id
        recipe = get_object_or_404(Recipes, id=recipe_id)
        serializer = RecipesUserSerializer(recipe)
        return serializer.data


class Base64ImageField(serializers.ImageField):
    """Обработка изображения кодирование Base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Тегов."""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")
        validators = (
            UniqueTogetherValidator(
                queryset=Tag.objects.all(), fields=("name", "color", "slug")
            ),
        )


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода информации о списке или отдельном рецепте."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientsRecipeSerializer(source="recipe", many=True)
    is_favorited = serializers.SerializerMethodField(
        method_name="get_is_favorited"
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name="get_is_in_shopping_cart"
    )

    class Meta:
        model = Recipes
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "text",
            "image",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        context = self.context
        if "request" in context:
            user = context["request"].user
        if user.is_authenticated:
            recipe = obj.id
            return Favorite.objects.filter(
                user=user, recipe_id=recipe
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        context = self.context
        if "request" in context:
            user = context["request"].user
        if user.is_authenticated:
            recipe = obj.id
            return ShoppingCart.objects.filter(
                user=user, recipe_id=recipe
            ).exists()
        return False


class RecipesCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания/изменения/удаления отдельного рецепта."""

    author = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientsCreateRecipeSerializer(many=True, source="recipe")
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(
        validators=(MinValueValidator(MIN_TIME),)
    )

    class Meta:
        model = Recipes
        fields = "__all__"
        validators = (
            UniqueTogetherValidator(
                queryset=Recipes.objects.all(),
                fields=("author", "name"),
                message="Нельзя публиковать одинаковые рецепты",
            ),
        )

    @transaction.atomic
    def create(self, validated_data):
        with transaction.atomic():
            validated_data["author"] = self.context["request"].user
            ingredients_data = validated_data.pop("recipe")
            tag_data = validated_data.pop("tags")
            new_recipe = Recipes.objects.create(**validated_data)
            new_recipe.tags.set(tag_data)
            for ingredient in ingredients_data:
                IngredientsRecipe.objects.create(
                    recipe=new_recipe,
                    ingredient=get_object_or_404(
                        Ingredients, id=ingredient.get("id")
                    ),
                    amount=ingredient.get("amount"),
                )
        return new_recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("recipe")
        tag_data = validated_data.pop("tags")
        instance.pub_date = validated_data.get("pub_date", instance.pub_date)
        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.save()
        IngredientsRecipe.objects.filter(recipe__id=instance.id).delete()
        for ingredient in ingredients_data:
            if "id" in ingredient:
                IngredientsRecipe.objects.create(
                    recipe_id=instance.id,
                    ingredient=get_object_or_404(
                        Ingredients, id=ingredient.get("id")
                    ),
                    amount=ingredient.get("amount"),
                )
        instance.tags.set(tag_data)
        return instance

    def to_representation(self, instance):
        recipe_id = instance.id
        recipe = get_object_or_404(Recipes, id=recipe_id)
        serializer = RecipesSerializer(recipe, context=self.context)
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор добавления/удаления рецепта из списка избранного."""

    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    recipe = serializers.SerializerMethodField(method_name="get_recipe")

    class Meta:
        model = Favorite
        fields = ("user", "recipe")

    def get_recipe(self, obj):
        recipe_id = self.instance.id
        return recipe_id

    def validate(self, data):
        my_view = self.context["view"]
        recipe_id = my_view.kwargs.get("id")
        current_user = self.context["request"].user
        recipe = get_object_or_404(Recipes, id=recipe_id)
        if Favorite.objects.filter(user=current_user, recipe=recipe).exists():
            raise serializers.ValidationError(
                "Вы уже добавили этот рецепт в избранное."
            )
        return data

    def to_representation(self, instance):
        recipe_id = instance.recipe.id
        recipe = get_object_or_404(Recipes, id=recipe_id)
        serializer = RecipesUserSerializer(recipe)
        return serializer.data
