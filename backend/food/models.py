from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from backend.settings import MIN_VALUE


class User(AbstractUser):

    username = models.CharField(
        max_length=150,
        null=True,
        unique=True,
        verbose_name='Логин',
        help_text='Укажите логин'
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='Email',
        help_text='Укажите адрес электронной почты'
    )
    first_name = models.CharField(
        max_length=150,
        null=True,
        verbose_name='Имя',
        help_text='Укажите имя'
    )
    last_name = models.CharField(
        max_length=150,
        null=True,
        verbose_name='Фамилия',
        help_text='Укажите фамилию'
    )

    password = models.CharField(
        max_length=150,
        null=True,
        verbose_name='Пароль',
        help_text='Укажите пароль'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username', 'first_name', 'last_name'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название',
                            help_text='Укажите название')
    color = models.CharField(max_length=7, verbose_name='Цвет',
                             help_text='Укажите цвет')
    slug = models.SlugField(unique=True, verbose_name='Slug',
                            help_text='Укажите Slug')

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название',
                            help_text='Укажите название')
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Ед. измерения',
                                        help_text='Укажите ед. измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    tags = models.ManyToManyField(Tag, verbose_name='Теги',
                                  help_text='Укажите теги')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор', help_text='Укажите автора рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredients, through='IngredientsRecipe',
        verbose_name='Ингредиенты', help_text='Укажите ингредиенты'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True,
        help_text='Укажите дату'
    )
    name = models.CharField(max_length=200, verbose_name='Название',
                            help_text='Укажите название')
    image = models.ImageField(verbose_name='Картинка',
                              help_text='Добавьте картинку')
    text = models.TextField(verbose_name='Описание',
                            help_text='Добавьте описание')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            MIN_VALUE,
            message=f'Время приготовления должно быть не менее {MIN_VALUE}')],
        verbose_name='Время приготовления', help_text='Укажите время готовки'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'name'),
                name='author_recipe_name_unique',
            )]
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientsRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, related_name='recipe',
        verbose_name='Рецепт', help_text='Укажите рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE, related_name='in_recipe',
        verbose_name='Ингредиент', help_text='Укажите ингредиент'
    )
    amount = models.IntegerField(validators=[
        MinValueValidator(
            MIN_VALUE,
            message=f'Минимальное кол-во должно быть не меньше {MIN_VALUE}!')],
        verbose_name='Кол-во', help_text='Укажите количество'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='recipe_ingredients_unique',
            )]
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'

    def __str__(self):
        return self.ingredient.name


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             help_text='Укажите пользователя',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, related_name='shopping_cart',
        help_text='Укажите рецепт', verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_shopping_cart'
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return self.recipe


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             help_text='Укажите пользователя',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, related_name='favorites',
        help_text='Укажите рецепт', verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_favorite'
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return self.recipe


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
        help_text='Укажите подписчика', verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        help_text='Укажите автора', verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_user_author'
            )
        ]
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return self.author.username
