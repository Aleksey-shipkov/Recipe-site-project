# Generated by Django 2.2.16 on 2022-11-19 12:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("food", "0004_auto_20221118_1107"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tag",
            options={
                "ordering": ("id",),
                "verbose_name": "Тег",
                "verbose_name_plural": "Теги",
            },
        ),
        migrations.AlterField(
            model_name="shoppingcart",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shopping_cart",
                to="food.Recipes",
            ),
        ),
    ]
