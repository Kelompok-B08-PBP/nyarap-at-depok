# Generated by Django 5.1.4 on 2024-12-19 10:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nyarap_nanti', '0003_remove_wishlistitem_user_wishlistitem_wishlist'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wishlistitem',
            name='wishlist',
        ),
        migrations.AddField(
            model_name='wishlistitem',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
