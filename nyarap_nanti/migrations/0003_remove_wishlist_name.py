# Generated by Django 4.2.16 on 2024-10-26 18:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nyarap_nanti', '0002_wishlist_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wishlist',
            name='name',
        ),
    ]
