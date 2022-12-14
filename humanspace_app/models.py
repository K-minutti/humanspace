from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):
    """A topic a user is learning about"""
    topic = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        """Return a string representation of the model."""
        return self.topic


class Entry(models.Model):
    """A learning entry linked to a topic"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'entries'

    def __str__(self):
        """Return a string representation of the model"""
        return f"{self.text[:50]}..."

