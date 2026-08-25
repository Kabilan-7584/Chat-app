from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import SignupForm


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("accounts:home")

    else:
        form = SignupForm()

    return render(
        request,
        "accounts/signup.html",
        {"form": form},
    )


def accounts_home(request):
    return render(
        request,
        "accounts/home.html",
    )


@login_required
def protected_test_view(request):
    return render(
        request,
        "accounts/protected.html",
    )