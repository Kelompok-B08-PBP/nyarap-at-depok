from django.db import models
from django.contrib.auth.models import User  # Jika ada sistem pengguna

class Detailer(models.Model):
    name = models.CharField(max_length=255, default="no name")  # Nama produk
    restaurant = models.CharField(max_length=255, default="no name")  # Nama restoran
    rating = models.FloatField(default=0)  # Rating restoran
    operational_hours = models.CharField(max_length=100, default="no name")  # Jam operasional
    location = models.CharField(max_length=255, default="no name")  # Lokasi
    price = models.IntegerField(default=0)  # Harga
    image = models.URLField(default="no images")  # Link foto produk
    def __str__(self):
        return self.resto_name

class Comment(models.Model):
    name = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    detailer = models.ForeignKey(Detailer, on_delete=models.CASCADE)

    def __str__(self):
        return f'Comment by {self.name} on {self.detailer.resto_name}'


