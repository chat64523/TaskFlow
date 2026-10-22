from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ProjectForm, ProjectMemberForm
from .models import Project, ProjectMembership


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
    if request.user.role != "MANAGER" and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.manager = request.user
            project.save()

            messages.success(
                request,
                f'Project "{project.name}" was created successfully.',
            )

            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm()

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
