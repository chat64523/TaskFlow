from django.urls import path
from . import views


app_name = "projects"
urlpatterns = [
    path("", views.project_list_view, name="list"),
    path("create/", views.project_create_view, name="create"),
    path("<int:pk>/", views.project_detail_view, name="detail"),
    path("<int:pk>/edit/", views.project_update_view, name="update"),
    path(
        "<int:pk>/members/",
        views.project_members_view,
        name="members",
    ),
        path(
            "<int:pk>/delete/",
            views.project_delete_view,
            name="delete",
        ),
]
