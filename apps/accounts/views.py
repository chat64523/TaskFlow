from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import (
    AdminUserUpdateForm,
    LoginForm,
    ProfileUpdateForm,
    SignUpForm,
)
from .models import User


class EmailLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created.")
            return redirect("core:dashboard")
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})


@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})


@login_required
def password_change_view(request):
    from django.contrib.auth.forms import PasswordChangeForm

    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect("accounts:profile")
    else:
        form = PasswordChangeForm(request.user)

    return render(
        request,
        "accounts/password_change.html",
        {"form": form},
    )


@login_required
def logout_view(request):
    if request.method != "POST":
        return redirect("core:dashboard")

    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("accounts:login")


def is_admin(user):
    return user.is_authenticated and (
        user.is_superuser or user.role == User.Role.ADMIN
    )


@user_passes_test(is_admin)
def admin_user_list_view(request):
    users = User.objects.all().order_by("email")
    return render(request, "accounts/admin_user_list.html", {"users": users})


@user_passes_test(is_admin)
def admin_user_update_view(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        form = AdminUserUpdateForm(request.POST, instance=target_user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully.")
            return redirect("accounts:admin-users")
    else:
        form = AdminUserUpdateForm(instance=target_user)

    return render(
        request,
        "accounts/admin_user_update.html",
        {"form": form, "target_user": target_user},
    )
