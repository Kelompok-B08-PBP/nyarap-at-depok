# Generated by Django 5.1.2 on 2024-10-23 09:08

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_userpreference_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpreference',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userpreference',
            name='preferred_breakfast_type',
            field=models.CharField(choices=[('masih_bingung', 'Masih Bingung'), ('nasi', 'Nasi'), ('roti', 'Roti'), ('lontong', 'Lontong'), ('cemilan', 'Cemilan'), ('minuman', 'Minuman')], max_length=100),
        ),
        migrations.AlterField(
            model_name='userpreference',
            name='preferred_location',
            field=models.CharField(choices=[('beji', 'Beji'), ('bojongsari', 'Bojongsari'), ('cilodong', 'Cilodong'), ('cimanggis', 'Cimanggis'), ('cinere', 'Cinere'), ('cipayung', 'Cipayung'), ('limo', 'Limo'), ('pancoran_mas', 'Pancoran Mas'), ('sawangan', 'Sawangan'), ('sukmajaya', 'Sukmajaya'), ('tapos', 'Tapos')], max_length=255),
        ),
        migrations.AlterField(
            model_name='userpreference',
            name='preferred_price_range',
            field=models.CharField(choices=[('0-15000', 'Dibawah Rp 15.000'), ('15000-25000', 'Rp 15.000 - Rp 25.000'), ('25000-50000', 'Rp 25.000 - Rp 50.000'), ('50000-100000', 'Rp 50.000 - Rp 100.000'), ('100000+', 'Diatas Rp 100.000')], max_length=50),
        ),
    ]