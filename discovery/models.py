from django.db import models
from django.contrib.auth.models import User

class PostEntry(models.Model):
    title = models.CharField(max_length=200)
    caption = models.TextField()
    location = models.CharField(max_length=100)
    photo_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True  # Tambahkan ini untuk memastikan kompatibilitas dengan data lama
    )

    def __str__(self):
        return f"{self.title} by {self.user.username if self.user else 'Unknown'}"