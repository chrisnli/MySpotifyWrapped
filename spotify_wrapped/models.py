"""
Database models and associated functions, which allow our web app to
effectively communicate with our database backend.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Account(models.Model):
    """
    A representation of a user's account, which contains a one-to-one
    relationship with a Django User. Allows us to extend Django users with
    additional fields.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    @classmethod
    def new(cls, username, password):
        """
        Creates and saves a new user and account to the database
        Does not do any checking on the username or password before passing
        them to the User model - that should be done before calling this
        function
        :param username: The username for the new user
        :param password: The password for the new user
        """
        user = User.objects.create_user(username=username, password=password)
        user.save()
        account = Account.objects.create(user=user)
        account.save()
        return account
