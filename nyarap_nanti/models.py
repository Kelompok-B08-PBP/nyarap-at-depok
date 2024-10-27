# models.py
from django.db import models
from django.contrib.auth.models import User
from main.models import Restaurant




class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Collection(models.Model):
    wishlist = models.ForeignKey(Wishlist, related_name='collections', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.wishlist.user.username}"

class CollectionItem(models.Model):
    collection = models.ForeignKey(Collection, related_name='items', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.restaurant.name} in {self.collection.name}"
    

