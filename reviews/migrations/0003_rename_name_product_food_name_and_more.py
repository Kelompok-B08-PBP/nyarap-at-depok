# Generated by Django 5.1.2 on 2024-10-25 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_alter_product_options_remove_product_time_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='name',
            new_name='food_name',
        ),
        migrations.RemoveField(
            model_name='product',
            name='keywords',
        ),
        migrations.AddField(
            model_name='product',
            name='restaurant_name',
            field=models.CharField(default='Unknown Restaurant', max_length=255),
        ),
    ]
