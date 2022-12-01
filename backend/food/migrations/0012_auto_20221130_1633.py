# Generated by Django 2.2.16 on 2022-11-30 13:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0011_auto_20221128_1933'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredients',
            options={'ordering': ('name',), 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'verbose_name': 'Список покупок', 'verbose_name_plural': 'Список покупок'},
        ),
        migrations.AlterModelOptions(
            name='subscriptions',
            options={'verbose_name': 'Подписки', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('name',), 'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
    ]