import uuid
from django.db import models
from django.contrib.auth.models import User

class UserPreference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    preferred_location = models.CharField(max_length=255, blank=True)
    preferred_breakfast_type = models.CharField(max_length=100, blank=True)
    preferred_price_range = models.CharField(max_length=50, blank=True)

