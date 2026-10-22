from apps.accounts.models import User
from apps.projects.models import Project, ProjectMembership


class ProjectPermissions:
    """
    Centralized authorization rules for project-related actions.
    """

    @staticmethod
    def is_admin(user):
        return (
            user.is_authenticated
            and (
                user.is_superuser
                or user.role == User.Role.ADMIN
            )
        )

    @staticmethod
    def is_manager(user):
        return (
            user.is_authenticated
            and user.role == User.Role.MANAGER
        )

    @staticmethod
    def is_member(user):
        return (
            user.is_authenticated
            and user.role == User.Role.MEMBER
        )

    @staticmethod
    def can_view_project(user, project):
        """
        Admins can view every project.

        Managers can view projects they manage.

        Members can view projects they belong to.
        """

        if not user.is_authenticated:
            return False

        if ProjectPermissions.is_admin(user):
            return True

        if project.manager_id == user.id:
            return True

        return ProjectMembership.objects.filter(
            project=project,
            user=user,
        ).exists()

    @staticmethod
    def can_create_project(user):
        """
        Admins and Managers can create projects.
        """

        return (
            ProjectPermissions.is_admin(user)
            or ProjectPermissions.is_manager(user)
        )

    @staticmethod
    def can_edit_project(user, project):
        """
        Admins can edit any project.

        The Manager of a project can edit it.

        Members cannot edit project details.
        """

        if ProjectPermissions.is_admin(user):
            return True

        return (
            ProjectPermissions.is_manager(user)
            and project.manager_id == user.id
        )

    @staticmethod
    def can_delete_project(user, project):
        """
        Admins can delete any project.

        A project's Manager can delete their own project.
        """

        if ProjectPermissions.is_admin(user):
            return True

        return (
            ProjectPermissions.is_manager(user)
            and project.manager_id == user.id
        )

    @staticmethod
    def can_manage_members(user, project):
        """
        Admins can manage members globally.

        The Manager of a project can manage its members.
        """

        if ProjectPermissions.is_admin(user):
            return True

        return (
            ProjectPermissions.is_manager(user)
            and project.manager_id == user.id
        )

    @staticmethod
    def can_access_project_as_member(user, project):
        """
        Returns whether a user is a member of the project.
        """

        if not user.is_authenticated:
            return False

        return ProjectMembership.objects.filter(
            project=project,
            user=user,
        ).exists()
