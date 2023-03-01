from django.db import models


class GoogleTokens(models.Model):
    """
    
    """
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    ip = models.CharField(max_length=225)
