# Generated by Django 2.2.16 on 2022-10-16 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=7, null=True, verbose_name='Цвет тега'),
        ),
    ]