# Generated by Django 2.2.16 on 2022-11-16 16:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("food", "0002_auto_20221116_1700"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="recipes",
            options={
                "ordering": ("-pub_date",),
                "verbose_name": "Рецепт",
                "verbose_name_plural": "Рецепты",
            },
        ),
    ]
