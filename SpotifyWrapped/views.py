from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.urls import reverse

def index(request):
    return render(request, "SpotifyWrapped/homepage.html")

def account_creation(request):
    if request.method != 'POST':
        return render(request, "registration/register.html", {"form":UserCreationForm})
    else:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "registration/register.html", {"form": form})
