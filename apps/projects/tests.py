from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from apps.core.permissions import ProjectPermissions
from apps.projects.models import Project, ProjectMembership

User = get_user_model()


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
            email="othermanager@test.com",
            password="TestPass123!",
            role=User.Role.MANAGER,
        )
        self.member = User.objects.create_user(
            email="member@test.com",
            password="TestPass123!",
            role=User.Role.MEMBER,
        )
        self.non_member = User.objects.create_user(
            email="nonmember@test.com",
            password="TestPass123!",
            role=User.Role.MEMBER,
        )

        self.project = Project.objects.create(
            name="Test Project",
            description="Project test",
            manager=self.manager,
        )

        ProjectMembership.objects.create(
            project=self.project,
            user=self.member,
            invited_by=self.manager,
        )

    def test_admin_can_view_any_project(self):
        self.assertTrue(
            ProjectPermissions.can_view_project(self.admin, self.project)
        )

    def test_manager_can_view_own_project(self):
        self.assertTrue(
            ProjectPermissions.can_view_project(self.manager, self.project)
        )

    def test_other_manager_cannot_view_project(self):
        self.assertFalse(
            ProjectPermissions.can_view_project(
                self.other_manager, self.project
            )
        )

    def test_member_can_view_joined_project(self):
        self.assertTrue(
            ProjectPermissions.can_view_project(self.member, self.project)
        )

    def test_non_member_cannot_view_project(self):
        self.assertFalse(
            ProjectPermissions.can_view_project(
                self.non_member, self.project
            )
        )

    def test_admin_and_manager_can_create_projects(self):
        self.assertTrue(ProjectPermissions.can_create_project(self.admin))
        self.assertTrue(ProjectPermissions.can_create_project(self.manager))

    def test_member_cannot_create_project(self):
        self.client.force_login(self.member)

        response = self.client.post(
            reverse("projects:create"),
            {"name": "Forbidden Project", "description": ""},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("projects:list"))

        self.assertFalse(
            Project.objects.filter(name="Forbidden Project").exists()
        )

        messages = list(response.wsgi_request._messages)
        self.assertTrue(
            any(
                "permission to create projects" in str(message).lower()
                for message in messages
            )
        )

    def test_admin_can_edit_and_delete_project(self):
        self.assertTrue(
            ProjectPermissions.can_edit_project(self.admin, self.project)
        )
        self.assertTrue(
            ProjectPermissions.can_delete_project(self.admin, self.project)
        )

    def test_manager_can_edit_and_delete_own_project(self):
        self.assertTrue(
            ProjectPermissions.can_edit_project(self.manager, self.project)
        )
        self.assertTrue(
            ProjectPermissions.can_delete_project(self.manager, self.project)
        )

    def test_other_manager_cannot_edit_or_delete_project(self):
        self.assertFalse(
            ProjectPermissions.can_edit_project(
                self.other_manager, self.project
            )
        )
        self.assertFalse(
            ProjectPermissions.can_delete_project(
                self.other_manager, self.project
            )
        )

    def test_member_cannot_edit_or_delete_project(self):
        self.assertFalse(
            ProjectPermissions.can_edit_project(self.member, self.project)
        )
        self.assertFalse(
            ProjectPermissions.can_delete_project(self.member, self.project)
        )

    def test_only_admin_or_project_manager_can_manage_members(self):
        self.assertTrue(
            ProjectPermissions.can_manage_members(self.admin, self.project)
        )
        self.assertTrue(
            ProjectPermissions.can_manage_members(self.manager, self.project)
        )
        self.assertFalse(
            ProjectPermissions.can_manage_members(
                self.other_manager, self.project
            )
        )
        self.assertFalse(
            ProjectPermissions.can_manage_members(self.member, self.project)
        )


class ProjectViewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="viewadmin@test.com",
            password="TestPass123!",
            role=User.Role.ADMIN,
        )
        self.manager = User.objects.create_user(
            email="viewmanager@test.com",
            password="TestPass123!",
            role=User.Role.MANAGER,
        )
        self.other_manager = User.objects.create_user(
            email="viewothermanager@test.com",
            password="TestPass123!",
            role=User.Role.MANAGER,
        )
        self.member = User.objects.create_user(
            email="viewmember@test.com",
            password="TestPass123!",
            role=User.Role.MEMBER,
        )
        self.non_member = User.objects.create_user(
            email="viewnonmember@test.com",
            password="TestPass123!",
            role=User.Role.MEMBER,
        )

        self.project = Project.objects.create(
            name="Managed Project",
            description="View test",
            manager=self.manager,
        )
        ProjectMembership.objects.create(
            project=self.project,
            user=self.member,
            invited_by=self.manager,
        )

    def test_manager_can_create_project(self):
        self.client.force_login(self.manager)
        response = self.client.post(
            reverse("projects:create"),
            {"name": "New Project", "description": "Created in test"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Project.objects.filter(
                name="New Project", manager=self.manager
            ).exists()
        )

    def test_member_cannot_create_project(self):
        self.client.force_login(self.member)

        response = self.client.post(
            reverse("projects:create"),
            {"name": "Forbidden Project", "description": ""},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("projects:list"))

        self.assertFalse(
            Project.objects.filter(name="Forbidden Project").exists()
        )

        messages = list(response.wsgi_request._messages)
        self.assertTrue(
            any("permission" in str(message).lower() for message in messages)
        )

    def test_manager_cannot_edit_another_managers_project(self):
        self.client.force_login(self.other_manager)
        response = self.client.get(
            reverse("projects:update", args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_member_cannot_edit_project(self):
        self.client.force_login(self.member)
        response = self.client.get(
            reverse("projects:update", args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_member_cannot_view_unjoined_project(self):
        self.client.force_login(self.non_member)
        response = self.client.get(
            reverse("projects:detail", args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_member_can_view_joined_project(self):
        self.client.force_login(self.member)
        response = self.client.get(
            reverse("projects:detail", args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_admin_can_view_project_list(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)


    def test_manager_can_delete_own_project(self):
        self.client.force_login(self.manager)

        response = self.client.post(
            reverse("projects:delete", args=[self.project.pk])
        )

        self.assertRedirects(response, reverse("projects:list"))
        self.assertFalse(
            Project.objects.filter(pk=self.project.pk).exists()
        )

    def test_admin_can_delete_any_project(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("projects:delete", args=[self.project.pk])
        )

        self.assertRedirects(response, reverse("projects:list"))
        self.assertFalse(
            Project.objects.filter(pk=self.project.pk).exists()
        )

    def test_other_manager_cannot_delete_project(self):
        self.client.force_login(self.other_manager)

        response = self.client.post(
            reverse("projects:delete", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Project.objects.filter(pk=self.project.pk).exists()
        )

    def test_member_cannot_delete_project(self):
        self.client.force_login(self.member)

        response = self.client.post(
            reverse("projects:delete", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Project.objects.filter(pk=self.project.pk).exists()
        )


    def test_get_request_cannot_delete_project(self):
        self.client.force_login(self.manager)

        response = self.client.get(
            reverse("projects:delete", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(
            Project.objects.filter(pk=self.project.pk).exists()
        )
