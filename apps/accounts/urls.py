from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    EmailLoginView,
    admin_user_list_view,
    admin_user_update_view,
    logout_view,
    password_change_view,
    profile_view,
    signup_view,
)

app_name = "accounts"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", EmailLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("password-change/", password_change_view, name="password-change"),
    path("admin/users/", admin_user_list_view, name="admin-users"),
    path(
        "admin/users/<int:user_id>/edit/",
        admin_user_update_view,
        name="admin-user-edit",
    ),
]
