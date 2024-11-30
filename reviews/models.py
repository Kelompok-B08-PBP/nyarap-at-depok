from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant_name = models.CharField(max_length=255, default="Unknown Restaurant") 
    food_name = models.CharField(max_length=255) 
    review = models.TextField()  # Review produk
    rating = models.IntegerField(default=0)  # Rating dengan 5 stars
    date_added = models.DateTimeField(default=timezone.now)  # Waktu saat membuat review
    product_identifier = models.CharField(max_length=255)  # ID produk
    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.restaurant_name} - {self.food_name} by {self.user.username}"

 