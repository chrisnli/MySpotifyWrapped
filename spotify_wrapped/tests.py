"""
Contains tests for functionality of the various functions in our web app
"""
from django.test import TestCase
from django.contrib.auth.models import User

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
