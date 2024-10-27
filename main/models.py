import uuid
from django.db import models
from django.contrib.auth.models import User

class UserPreference(models.Model):
    KECAMATAN_CHOICES = [
        ('Beji', 'Beji'),
        ('bojongsari', 'Bojongsari'),
        ('cilodong', 'Cilodong'),
        ('cimanggis', 'Cimanggis'),
        ('cinere', 'Cinere'),
        ('cipayung', 'Cipayung'),
        ('limo', 'Limo'),
        ('pancoran_mas', 'Pancoran Mas'),
        ('sawangan', 'Sawangan'),
        ('sukmajaya', 'Sukmajaya'),
        ('tapos', 'Tapos'),
    ]

    BREAKFAST_CHOICES = [
        ('masih_bingung', 'Masih Bingung'),
        ('nasi', 'Nasi'),
        ('roti', 'Roti'),
        ('lontong', 'Lontong'),
        ('cemilan', 'Cemilan'),
        ('minuman', 'Minuman'),
    ]

    PRICE_CHOICES = [
        ('0-15000', 'Dibawah Rp 15.000'),
        ('15000-25000', 'Rp 15.000 - Rp 25.000'),
        ('25000-50000', 'Rp 25.000 - Rp 50.000'),
        ('50000-100000', 'Rp 50.000 - Rp 100.000'),
        ('100000+', 'Diatas Rp 100.000'),
    ]

    def __str__(self):
        return f"{self.user.username}'s Preferences"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    preferred_location = models.CharField(max_length=255, choices=KECAMATAN_CHOICES)
    preferred_breakfast_type = models.CharField(max_length=100, choices=BREAKFAST_CHOICES)
    preferred_price_range = models.CharField(max_length=50, choices=PRICE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Menghubungkan dengan preferensi pengguna
    product_identifier = models.CharField(max_length=255)  # Gunakan ID unik produk
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on Product {self.product_identifier}"