"""
Contains tests for functionality of the various functions in our web app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from spotify_wrapped.models import Account

User = get_user_model()

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
