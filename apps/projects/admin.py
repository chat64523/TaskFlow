from django.contrib import admin
from .models import Project, ProjectMembership


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "manager", "created_at", "updated_at")
    search_fields = ("name", "description", "manager__email")
    list_filter = ("created_at",)
    inlines = [ProjectMembershipInline]


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "invited_by", "joined_at")
    search_fields = ("project__name", "user__email")
    list_filter = ("joined_at",)
