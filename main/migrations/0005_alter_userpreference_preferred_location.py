# Generated by Django 5.1.2 on 2024-10-25 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_userpreference_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpreference',
            name='preferred_location',
            field=models.CharField(choices=[('Beji', 'Beji'), ('bojongsari', 'Bojongsari'), ('cilodong', 'Cilodong'), ('cimanggis', 'Cimanggis'), ('cinere', 'Cinere'), ('cipayung', 'Cipayung'), ('limo', 'Limo'), ('pancoran_mas', 'Pancoran Mas'), ('sawangan', 'Sawangan'), ('sukmajaya', 'Sukmajaya'), ('tapos', 'Tapos')], max_length=255),
        ),
    ]
