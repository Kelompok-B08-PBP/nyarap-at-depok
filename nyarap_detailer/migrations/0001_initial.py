# Generated by Django 5.1.2 on 2024-10-27 14:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Detailer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='no name', max_length=255)),
                ('restaurant', models.CharField(default='no name', max_length=255)),
                ('rating', models.FloatField(default=0)),
                ('operational_hours', models.CharField(default='no name', max_length=100)),
                ('location', models.CharField(default='no name', max_length=255)),
                ('price', models.IntegerField(default=0)),
                ('image', models.URLField(default='no images')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('detailer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nyarap_detailer.detailer')),
            ],
        ),
    ]
