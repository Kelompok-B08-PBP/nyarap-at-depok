from django.db import models
from django.contrib.auth.models import User  # Jika ada sistem pengguna

class Detailer(models.Model):
    resto_name = models.CharField(max_length=200)
    description = models.TextField()
    time = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    rating = models.DecimalField(max_digits=2, decimal_places=1)

    def __str__(self):
        return self.resto_name

class Comment(models.Model):
    name = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    detailer = models.ForeignKey(Detailer, on_delete=models.CASCADE)

    def __str__(self):
        return f'Comment by {self.name} on {self.detailer.resto_name}'


