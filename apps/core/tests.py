from django.test import TestCase

from apps.accounts.models import User
from apps.core.permissions import ProjectPermissions
from apps.projects.models import Project, ProjectMembership


class ProjectPermissionsTests(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="TestPass123!",
            role=User.Role.ADMIN,
        )

        self.manager = User.objects.create_user(
            email="manager@test.com",
            password="TestPass123!",
            role=User.Role.MANAGER,
        )

        self.other_manager = User.objects.create_user(
            email="other-manager@test.com",
            password="TestPass123!",
            role=User.Role.MANAGER,
        )

        self.member = User.objects.create_user(
            email="member@test.com",
            password="TestPass123!",
            role=User.Role.MEMBER,
        )

        self.non_member = User.objects.create_user(
            email="non-member@test.com",
            password="TestPass123!",
            role=User.Role.MEMBER,
        )

        self.project = Project.objects.create(
            name="Test Project",
            description="Authorization test project",
            manager=self.manager,
        )

        ProjectMembership.objects.create(
            project=self.project,
            user=self.member,
            invited_by=self.manager,
        )

    def test_admin_can_view_any_project(self):
        self.assertTrue(
            ProjectPermissions.can_view_project(
                self.admin,
                self.project,
            )
        )

    def test_manager_can_view_own_project(self):
        self.assertTrue(
            ProjectPermissions.can_view_project(
                self.manager,
                self.project,
            )
        )

    def test_member_can_view_project_they_belong_to(self):
        self.assertTrue(
            ProjectPermissions.can_view_project(
                self.member,
                self.project,
            )
        )

    def test_non_member_cannot_view_project(self):
        self.assertFalse(
            ProjectPermissions.can_view_project(
                self.non_member,
                self.project,
            )
        )

    def test_admin_can_create_project(self):
        self.assertTrue(
            ProjectPermissions.can_create_project(self.admin)
        )

    def test_manager_can_create_project(self):
        self.assertTrue(
            ProjectPermissions.can_create_project(self.manager)
        )

    def test_member_cannot_create_project(self):
        self.assertFalse(
            ProjectPermissions.can_create_project(self.member)
        )

    def test_admin_can_edit_any_project(self):
        self.assertTrue(
            ProjectPermissions.can_edit_project(
                self.admin,
                self.project,
            )
        )

    def test_project_manager_can_edit_project(self):
        self.assertTrue(
            ProjectPermissions.can_edit_project(
                self.manager,
                self.project,
            )
        )

    def test_other_manager_cannot_edit_project(self):
        self.assertFalse(
            ProjectPermissions.can_edit_project(
                self.other_manager,
                self.project,
            )
        )

    def test_member_cannot_edit_project(self):
        self.assertFalse(
            ProjectPermissions.can_edit_project(
                self.member,
                self.project,
            )
        )

    def test_admin_can_delete_any_project(self):
        self.assertTrue(
            ProjectPermissions.can_delete_project(
                self.admin,
                self.project,
            )
        )

    def test_project_manager_can_delete_project(self):
        self.assertTrue(
            ProjectPermissions.can_delete_project(
                self.manager,
                self.project,
            )
        )

    def test_other_manager_cannot_delete_project(self):
        self.assertFalse(
            ProjectPermissions.can_delete_project(
                self.other_manager,
                self.project,
            )
        )

    def test_member_cannot_delete_project(self):
        self.assertFalse(
            ProjectPermissions.can_delete_project(
                self.member,
                self.project,
            )
        )

    def test_admin_can_manage_members(self):
        self.assertTrue(
            ProjectPermissions.can_manage_members(
                self.admin,
                self.project,
            )
        )

    def test_project_manager_can_manage_members(self):
        self.assertTrue(
            ProjectPermissions.can_manage_members(
                self.manager,
                self.project,
            )
        )

    def test_member_cannot_manage_members(self):
        self.assertFalse(
            ProjectPermissions.can_manage_members(
                self.member,
                self.project,
            )
        )
