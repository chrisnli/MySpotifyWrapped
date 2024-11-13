"""
Contains tests for functionality of the various functions in our web app
"""

from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from spotify_wrapped.models import Account, SingleWrapped

User = get_user_model()
with open("test_inputs/example_artists.json", "r", encoding="utf-8") as artists_file:
    example_artists = artists_file.read()
with open("test_inputs/example_tracks.json", "r", encoding="utf-8") as tracks_file:
    example_tracks = tracks_file.read()


class AccountCreationTests(TestCase):
    """
    Tests which relate to account creation
    """
    def test_account_creation_valid_account(self):
        """
        Test if a new account can be created successfully
        """
        response = self.client.post('/accounts/create', {
            "username": "test_account_creation_valid_account",
            "password1": "t3sT_p@ssword",
            "password2": "t3sT_p@ssword",
        }, follow=True)
        # Ensure redirects to homepage on successful login
        self.assertRedirects(response, '/')
        # Ensure user now exists in database
        User.objects.get(username="test_account_creation_valid_account")

    def test_account_creation_common_password(self):
        """
        Test if the login system rejects accounts with common passwords
        """
        response = self.client.post('/accounts/create', {
            "username": "test_account_creation_common_password",
            "password1": "password123",
            "password2": "password123",
        }, follow=True)
        # Ensure it returns the same page with the error text on unsuccessful login
        self.assertIs(response.status_code, 200)
        self.assertContains(response, "This password is too common.")
        # Ensure user has not been added to the database
        self.assertFalse(
            User.objects.filter(username="test_account_creation_common_password").exists(),
            "User was added to the database when they had a common password")

    def test_account_creation_same_username_password(self):
        """
        Test if the login system rejects accounts with the same username and password
        """
        response = self.client.post('/accounts/create', {
            "username": "test_account_creation_same_username_password",
            "password1": "test_account_creation_same_username_password",
            "password2": "test_account_creation_same_username_password",
        })
        # Ensure it returns the same page with the error text on unsuccessful login
        self.assertIs(response.status_code, 200)
        self.assertContains(response, "The password is too similar to the username.")
        # Ensure user has not been added to the database
        self.assertFalse(
            User.objects.filter(username="test_account_creation_same_username_password").exists(),
            "User was added to the database when they have the same name and password")

    def test_account_creation_get_request(self):
        """
        Test if the login system displays the correct page on a GET request
        """
        response = self.client.get('/accounts/create')
        # Ensure it returns the page without error
        self.assertIs(response.status_code, 200)
        # Ensure it loads the correct template
        self.assertTemplateUsed(response, 'registration/register.html')

class AccountDatabaseTests(TestCase):
    """
    Tests which relate to the Account model and its database interactions
    """
    def test_account_database_creation(self):
        """
        Ensures that the Account model can be created properly with a User
        """
        test_user = User.objects.create_user(username="test_account_database_creation")
        test_account = Account(user=test_user)
        self.assertEqual(test_user, test_account.user)
        self.assertEqual(test_user.account, test_account)

    def test_account_new_function(self):
        """
        Ensures that the Account new function properly creates a User and an Account
        """
        # No how the new function does not validate that the password is not
        # too common - must be done before calling new
        Account.new(username="test_account_new_function", password="password123")
        # Ensure user now exists in database
        user = User.objects.get(username="test_account_new_function")
        # Ensure account now exists in database
        Account.objects.get(user=user)

    def test_access_expired_not_expired(self):
        """
        Ensures an Account can properly determine that an access token has not
        expired
        """
        test_account = Account.new(username="test_access_expired_not_expired",
                                   password="password123")
        test_account.access_token_expiration_time = timezone.now() + timedelta(minutes=1)
        self.assertFalse(test_account.access_expired())

    def test_access_expired_expired(self):
        """
        Ensures an Account can properly determine that an access token has expired
        """
        test_account = Account.new(username="test_access_expired_not_expired",
                                   password="password123")
        test_account.access_token_expiration_time = timezone.now() - timedelta(minutes=1)
        self.assertTrue(test_account.access_expired())

    # Can't test web-based get methods until secrets module is merged

class SpotifyWrappedModelTests(TestCase):
    """
    Tests which related to the model representation of a SpotifyWrapped
    """
    def test_json_parse_slides(self):
        """
        Ensures we can properly parse the data from a JSON object returned from
        Spotify into a Wrapped with the correct slides
        """
        test_account = Account.new(username="test_json_parse", password="password123")
        wrapped_id = SingleWrapped.create(test_account, example_artists, example_tracks)
        wrapped = SingleWrapped.objects.get(id=wrapped_id)
        self.assertEqual(wrapped.get_slides(), [
            "Your number one artist was Artik & Asti!",
            "That makes you one of 1076226 fans!",
            "Your most played genre was russian pop!",
            "You have a niche taste in artists!",
            "Your number one song was Walk It Talk It!",
            "You tend to like mid-length songs.",
            "None of your top 5 songs were explicit 😇",
            "People may not have heard of the songs you like."
            + " All the more reason to share them!",
        ])

    def test_json_create_type(self):
        """
        Ensures we can properly parse the data from a JSON object returned from
        Spotify into a Wrapped with the correct type
        """
        test_account = Account.new(username="test_json_create_type", password="password123")
        wrapped_id = SingleWrapped.create(test_account, example_artists, example_tracks)
        wrapped = SingleWrapped.objects.get(id=wrapped_id)
        self.assertEqual(wrapped.get_type(), "Single Wrapped")

    def test_json_create_id(self):
        """
        Ensures we can properly parse the data from a JSON object returned from
        Spotify into a Wrapped with a valid id
        """
        test_account = Account.new(username="test_json_create_id", password="password123")
        wrapped_id = SingleWrapped.create(test_account, example_artists, example_tracks)
        wrapped = SingleWrapped.objects.get(id=wrapped_id)
        #This is kind of obviously correct but more tests never hurt in case
        #the implementation gets more complicated in the future
        self.assertEqual(wrapped.get_id(), str(wrapped_id))

    def test_json_create_datetime(self):
        """
        Ensures we can properly parse the data from a JSON object returned from
        Spotify into a Wrapped with the correct datetime (Within a few minutes so
        this test is not too precise to run consistently)
        """
        test_account = Account.new(username="test_json_create_datetime", password="password123")
        wrapped_id = SingleWrapped.create(test_account, example_artists, example_tracks)
        wrapped = SingleWrapped.objects.get(id=wrapped_id)
        datetime = wrapped.get_created_at()
        now = timezone.now()
        diff = now - datetime
        functional = diff < timedelta(minutes=3)
        self.assertTrue(functional, "The recorded datetime of the wrapped"
                        + " and the current time differ by more than 3 minutes")
