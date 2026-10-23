from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ProjectForm, ProjectMemberForm
from .models import Project, ProjectMembership
from django.db import IntegrityError, transaction
from apps.core.permissions import ProjectPermissions
from django.views.decorators.http import require_POST


@login_required
def project_list_view(request):
    user = request.user

    if user.is_superuser or user.role == "ADMIN":
        projects = Project.objects.select_related("manager").all()

    elif user.role == "MANAGER":
        projects = Project.objects.filter(
            manager=user
        ).select_related("manager")

    else:
        projects = Project.objects.filter(
            members=user
        ).select_related("manager")

    return render(
        request,
        "projects/project_list.html",
        {"projects": projects},
    )


@login_required
def project_detail_view(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("manager"),
        pk=pk,
    )

    user = request.user

    if (
        not user.is_superuser
        and user.role != "ADMIN"
        and project.manager_id != user.id
        and not project.members.filter(pk=user.pk).exists()
    ):
        raise PermissionDenied

    return render(
        request,
        "projects/project_detail.html",
        {"project": project},
    )


@login_required
def project_create_view(request):
    user = request.user

    if not ProjectPermissions.can_create_project(user):
        messages.info(
            request,
            "You do not have permission to create projects. "
            "Please contact an Admin or Manager for assistance.",
        )
        return redirect("projects:list")

    if request.method == "POST":
        form = ProjectForm(request.POST, user=user)

        if form.is_valid():
            project = form.save(commit=False)

            if ProjectPermissions.is_admin(user):
                if not project.manager_id:
                    form.add_error(
                        "manager",
                        "Please select a project Manager.",
                    )
                    return render(
                        request,
                        "projects/project_form.html",
                        {
                            "form": form,
                            "page_title": "Create Project",
                        },
                    )
            else:
                # A Manager automatically manages their own project.
                project.manager = user

            try:
                with transaction.atomic():
                    project.save()
            except IntegrityError:
                form.add_error(
                    "name",
                    "This Manager already has a project with this name.",
                )
            else:
                messages.success(
                    request,
                    f'Project "{project.name}" was created successfully.',
                )
                return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm(user=user)

    return render(
        request,
        "projects/project_form.html",
        {
            "form": form,
            "page_title": "Create Project",
        },
    )


@login_required
def project_update_view(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if (
        not request.user.is_superuser
        and request.user.role != "ADMIN"
        and project.manager_id != request.user.id
    ):
        raise PermissionDenied

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Project updated successfully.",
            )

            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "projects/project_form.html",
        {
            "form": form,
            "page_title": "Edit Project",
        },
    )


@login_required
def project_members_view(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if (
        not request.user.is_superuser
        and request.user.role != "ADMIN"
        and project.manager_id != request.user.id
    ):
        raise PermissionDenied

    current_members = project.members.all()

    if request.method == "POST":
        form = ProjectMemberForm(request.POST)

        if form.is_valid():
            selected_members = form.cleaned_data["members"]

            ProjectMembership.objects.filter(
                project=project
            ).exclude(
                user__in=selected_members
            ).delete()

            for member in selected_members:
                ProjectMembership.objects.get_or_create(
                    project=project,
                    user=member,
                    defaults={"invited_by": request.user},
                )

            messages.success(
                request,
                "Project members updated successfully.",
            )

            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectMemberForm(
            initial={
                "members": current_members,
            }
        )

    return render(
        request,
        "projects/project_members.html",
        {
            "project": project,
            "form": form,
        },
    )

@login_required
@require_POST
def project_delete_view(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if not ProjectPermissions.can_delete_project(request.user, project):
        raise PermissionDenied

    project_name = project.name
    project.delete()

    messages.success(
        request,
        f'Project "{project_name}" was deleted successfully.',
    )

    return redirect("projects:list")