"""
Database models and associated functions, which allow our web app to
effectively communicate with our database backend.
"""

from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    """
    A representation of a user's account, which contains a one-to-one
    relationship with a Django User. Allows us to extend Django users with
    additional fields.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
