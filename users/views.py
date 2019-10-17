from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import UserRegisterForm, UserUpdateForm


# Create your views here.
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # newuser = form.save()
            login(request, form.save())
            username = form.cleaned_data.get("username")
            messages.success(
                request,
                f"Your account has been created, {username}. You are now logged in",
                extra_tags="success",
            )
            messages.info(
                request,
                f"You can change your profile on this page, {username}.",
                extra_tags="info",
            )
            return redirect("profile")
        # else:
        #     messages.warning(request, f'Error')
        #     return redirect(request.path_info)
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Your account has been updated, {request.user.username}.",
                extra_tags="success",
            )
            return redirect("home-page")
    else:
        form = UserUpdateForm(instance=request.user)
    context = {"form": form}
    return render(request, "users/profile.html", context)
