import uuid
from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    name = models.CharField(max_length=255)  # Nama makanan
    time = models.DateField(auto_now_add=True) # Waktu saat membuat review
    review = models.TextField()  # Review produk
    rating = models.IntegerField(default=0)  # Rating produk

    def __str__(self):
        return self.name

 