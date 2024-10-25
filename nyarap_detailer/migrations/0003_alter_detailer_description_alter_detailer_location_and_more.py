# Generated by Django 5.1.2 on 2024-10-25 08:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nyarap_detailer', '0002_detailer_description_detailer_rating_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detailer',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='detailer',
            name='location',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='detailer',
            name='price',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='detailer',
            name='rating',
            field=models.DecimalField(decimal_places=2, max_digits=3),
        ),
        migrations.AlterField(
            model_name='detailer',
            name='resto_name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='detailer',
            name='time',
            field=models.CharField(max_length=100),
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
