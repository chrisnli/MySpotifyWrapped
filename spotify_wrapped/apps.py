"""
Module containing configuration options for this web app
"""
from django.apps import AppConfig

class SpotifyWrappedConfig(AppConfig):
    """
    Contains the configuration options for the spotify wrapped web app
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'spotify_wrapped'
