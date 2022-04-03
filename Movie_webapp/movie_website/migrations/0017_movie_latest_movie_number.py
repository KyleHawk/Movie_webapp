# Generated by Django 4.0.3 on 2022-04-01 21:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie_website', '0016_orders'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='latest',
            field=models.PositiveIntegerField(null=True, validators=[django.core.validators.MaxValueValidator(10)], verbose_name='Latest User Rating'),
        ),
        migrations.AddField(
            model_name='movie',
            name='number',
            field=models.IntegerField(default=100, verbose_name='Total Number of Rating'),
        ),
    ]
