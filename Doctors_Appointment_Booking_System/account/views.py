from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .templates import *

# Create your views here.

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, form.get_user())
            if user.is_superuser:
                 return redirect("admin:index")
            # else:
            #     return redirect("home")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})