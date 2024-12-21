# models.py

from django.db import models
from django.contrib.auth.models import User

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wishlist")

    def __str__(self):
        return f"Wishlist of {self.user.username}"
    
class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    restaurant = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    price = models.FloatField(default=0.0)
    rating = models.FloatField(default=0.0)
    operational_hours = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    
class WishlistNote(models.Model):
    wishlist_item = models.ForeignKey(WishlistItem, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Note for {self.wishlist_item.name}"
