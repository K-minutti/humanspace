from django.db import models


class Topic(models.Model):
    """A topic a user is learning about"""
    topic = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        """Return a string representation of the model."""
        return self.topic



