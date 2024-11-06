"""
Logic required to display correct web pages to users of our web app.
"""

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, get_user_model
from django.urls import reverse
from .models import Account

User = get_user_model()

def index(request):
    """
    :param request: The http request received
    :return: A HttpResponse for the index of our web app
    """
    return render(request, "spotify_wrapped/homepage.html")

def account_creation(request):
    """
    If the request uses the POST method with correct user creation data,
    creates a new user in the database and logs the new user in, sending them
    to the website home page. In other cases, it will redirect them to the
    signup page, displaying any errors with their previous account creation
    attempt if there are any.
    :param request: The http request received
    :return: A HttpResponse for our homepage if successful, or for the account
    creation page otherwise
    """
    if request.method != 'POST':
        return render(request, "registration/register.html", {"form":UserCreationForm})
    form = UserCreationForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        account = Account.new(username=username, password=password)
        login(request, account.user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "registration/register.html", {"form": form})
