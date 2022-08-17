from django.db import models
from django.contrib.auth.models import User

class TwitterAuthFlowState(models.Model):
    state = models.CharField(max_length=255)
    code_verifier = models.CharField(max_length=255)
    def __str__(self):
        return self.state
 

class TwitterAuthToken(models.Model):
    oauth_token = models.CharField(max_length=255)
    def __str__(self):
        return self.oauth_token


class TwitterUser(models.Model):
    twitter_id = models.CharField(max_length=255)
    screen_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    profile_image_url = models.CharField(max_length=255, null=True)
    twitter_oauth_token = models.ForeignKey(TwitterAuthToken, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.screen_name