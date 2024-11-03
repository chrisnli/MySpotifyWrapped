"""
Database models and associated functions, which allow our web app to
effectively communicate with our database backend.
"""

from datetime import timedelta
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import requests

User = get_user_model()

class Account(models.Model):
    """
    A representation of a user's account, which contains a one-to-one
    relationship with a Django User. Allows us to extend Django users with
    additional fields.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    access_token = models.TextField(null=True)
    access_token_expiration_time = models.DateTimeField(null=True)
    refresh_token = models.TextField(null=True)

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

    def access_expired(self):
        """
        :return: Whether the stored access token has expired
        """
        return timezone.now() > self.access_token_expiration_time

    def get_valid_access_token(self):
        """
        :return: The stored access token if it has not expired, otherwise
        refreshes the stored access token and returns that
        """
        if self.access_expired():
            self.refresh()
        return self.access_token

    def refresh(self):
        """
        Uses the stored refresh token to query a new access token, then
        stores the access token and the access token's expiration time
        """
        url = 'https://accounts.spotify.com/api/token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        body = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            # IMPORTANT: once secrets.py is in main, change this from being
            # just a string to being actual code
            'client_id': 'secrets.get_cli_id()',
        }
        response = requests.post(url, headers=headers, data=body, timeout=5)
        response_json = response.json()
        self.access_token = response_json['access_token']
        self.access_token_expiration_time = timezone.now() + timedelta(
            seconds=response_json['expires_in'])
