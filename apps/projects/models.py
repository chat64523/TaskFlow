from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="managed_projects",
        limit_choices_to={"role": "MANAGER"},
    )

    
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ProjectMembership",
        through_fields=("project", "user"),
        related_name="member_projects",
        blank=True,
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["manager", "name"],
                name="unique_project_name_per_manager",
            )
        ]

    def clean(self):
        super().clean()

        if self.manager_id and self.manager.role != "MANAGER":
            raise ValidationError({
                "manager": "The project manager must have the Manager role."
            })

    def __str__(self):
        return self.name


class ProjectMembership(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_invitations_sent",
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"],
                name="unique_project_membership",
            )
        ]
        ordering = ["joined_at"]

    def clean(self):
        super().clean()

        if self.user_id and self.project_id:
            if self.user.role == "ADMIN":
                raise ValidationError(
                    "Admins manage projects globally and do not need membership."
                )

            if self.user.role == "MANAGER":
                raise ValidationError(
                    "Only Members can be added as project members."
                )

    def __str__(self):
        return f"{self.user.email} - {self.project.name}"
