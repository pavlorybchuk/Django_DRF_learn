from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    """Chat room model."""
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Message(models.Model):
    """Chat message model - persisted to database."""
    room = models.ForeignKey(
        Room,
        related_name='messages',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        related_name='messages',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.user.username} [{self.timestamp:%Y-%m-%d %H:%M}]: {self.content[:50]}'