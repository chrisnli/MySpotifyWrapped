"""
Database models and associated functions, which allow our web app to
effectively communicate with our database backend.
"""

from datetime import timedelta
import json
import uuid
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

class SingleWrapped(models.Model):
    """Represents a spotify wrapped among a single person in the database"""
    id = models.TextField(primary_key=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    slides = models.JSONField()
    type = models.TextField(default='Single Wrapped')
    created_at = models.DateTimeField()

    @classmethod
    def parse(cls, user, artist_json, track_json):
        """
        Parses two jsons into a SingleWrapped object, but does NOT save it to
        the database
        :param user: The user who created this SingleWrapped
        :param artist_json: The json string returned from the spotify query of the top
         artists
        :param track_json: The json string returned from the spotify query of the top
        tracks
        :return: A SingleWrapped object with the data from both json strings
        """
        wrapped = SingleWrapped()
        wrapped.id = uuid.uuid4()
        wrapped.created_at = timezone.now()
        wrapped.user = user
        wrapped.slides = []
        artist_dict = json.loads(artist_json)
        top_artists = artist_dict["items"]
        if len(top_artists) == 0:
            wrapped.slides.append("You didn't listen to any music recently.")
            return wrapped
        _add_artists(wrapped.slides, top_artists)
        track_dict = json.loads(track_json)
        top_tracks = track_dict["items"]
        _add_tracks(wrapped.slides, top_tracks)
        return wrapped


    def get_slides(self):
        """
        :return: A list of all the pieces of text to display in this wrapped
        """
        return self.slides

    def get_type(self):
        """
        :return: A string representation of the type of this wrapped. Defaults to
        "Single Wrapped"
        """
        return self.type

    def get_created_at(self):
        """
        :return: The datetime at which this wrapped was created
        """
        return self.created_at

def _add_artists(slides, top_artists):
    slides.append("Your number one artist was " + str(top_artists[0]["name"]) + "!")
    slides.append("That makes you one of " +
                          str(top_artists[0]["followers"]["total"]) + " fans!")
    genre_counts = {}
    total_artist_popularity = 0
    for artist in top_artists:
        total_artist_popularity += int(artist["popularity"])
        genres = artist["genres"]
        for genre in genres:
            if genre in genre_counts:
                genre_counts[genre] += 1
            else:
                genre_counts[genre] = 1
    favorite_genre = max(genre_counts, key=genre_counts.get)
    if favorite_genre is None:
        slides.append(
            "Your favorite artists are so niche, we don't know what genre they are!")
    else:
        slides.append("Your most played genre was " + favorite_genre + "!")
    avg_artist_popularity = total_artist_popularity / len(top_artists)
    if avg_artist_popularity >= 80:
        slides.append("Everyone's on the same page about your favorite artists!")
    elif avg_artist_popularity >= 60:
        slides.append("Your favorite artists are interesting, but not controversial.")
    elif avg_artist_popularity >= 40:
        slides.append("You have a niche taste in artists!")
    elif avg_artist_popularity >= 20:
        slides.append("You tend to enjoy the smaller creators!")
    else:
        slides.append("Your taste in artists is quite unique!")

def _add_tracks(slides, top_tracks):
    slides.append("Your number one song was " + str(top_tracks[0]["name"]) + "!")
    total_length = 0
    total_explicit = 0
    total_track_popularity = 0
    for track in top_tracks:
        total_track_popularity += int(track["popularity"])
        total_length += int(track["duration_ms"])
        if track["explicit"] == "true":
            total_explicit += 1
    avg_length = total_length / len(top_tracks)
    avg_popularity = total_track_popularity / len(top_tracks)
    if avg_length <= 60000:
        slides.append("You tend to like shorter songs.")
    elif avg_length <= 240000:
        slides.append("You tend to like mid-length songs.")
    else:
        slides.append("You tend to like longer songs.")
    if total_explicit == 0:
        slides.append("None of your top 5 songs were explicit 😇")
    elif total_explicit <= 3:
        slides.append(str(total_explicit) + " of your top 5 songs were explicit.")
    else:
        slides.append("Oh my! " + str(total_explicit)
                              + " of your top 5 songs were explicit.")
    if avg_popularity >= 67:
        slides.append("The songs you listened to were popular all over!")
    elif avg_popularity >= 33:
        slides.append("Your playlist was a fresh change of pace for most people!")
    else:
        slides.append("The songs you listened to were very uncommon!")
