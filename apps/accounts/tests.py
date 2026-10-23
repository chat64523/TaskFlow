from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .forms import AdminUserUpdateForm, ProfileUpdateForm, SignUpForm

User = get_user_model()


class AccountTestBase(TestCase):
    def setUp(self):
        self.member = User.objects.create_user(
            email="member@example.com",
            password="TestPass123!",
            first_name="Test",
            last_name="Member",
            role=User.Role.MEMBER,
        )
        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="TestPass123!",
            role=User.Role.MANAGER,
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="TestPass123!",
        )


class SignUpTests(TestCase):
    def test_signup_page_loads(self):
        response = self.client.get(reverse("accounts:signup"))
        self.assertEqual(response.status_code, 200)

    def test_signup_creates_member_and_logs_them_in(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "email": "  NEWUSER@EXAMPLE.COM  ",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("core:dashboard"))

        user = User.objects.get(email="newuser@example.com")
        self.assertEqual(user.role, User.Role.MEMBER)
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_signup_rejects_duplicate_email(self):
        User.objects.create_user(
            email="existing@example.com",
            password="TestPass123!",
        )

        response = self.client.post(
            reverse("accounts:signup"),
            {
                "email": "existing@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            User.objects.filter(email="existing@example.com").count(), 1
        )


class LoginAndLogoutTests(AccountTestBase):
    def test_login_with_valid_email_and_password(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "member@example.com",
                "password": "TestPass123!",
            },
        )

        self.assertRedirects(response, reverse("core:dashboard"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_rejects_invalid_password(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "member@example.com",
                "password": "WrongPassword!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_post_logs_user_out(self):
        self.client.force_login(self.member)

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_get_does_not_log_user_out(self):
        self.client.force_login(self.member)

        response = self.client.get(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("core:dashboard"))
        self.assertIn("_auth_user_id", self.client.session)


class ProfileTests(AccountTestBase):
    def test_profile_requires_login(self):
        response = self.client.get(reverse("accounts:profile"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:profile')}",
        )

    def test_member_can_view_profile(self):
        self.client.force_login(self.member)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "member@example.com")

    def test_member_can_update_profile(self):
        self.client.force_login(self.member)

        response = self.client.post(
            reverse("accounts:profile"),
            {
                "first_name": "Updated",
                "last_name": "Name",
                "email": " UPDATED@EXAMPLE.COM ",
            },
        )

        self.assertRedirects(response, reverse("accounts:profile"))

        self.member.refresh_from_db()
        self.assertEqual(self.member.first_name, "Updated")
        self.assertEqual(self.member.last_name, "Name")
        self.assertEqual(self.member.email, "updated@example.com")

    def test_profile_rejects_an_email_used_by_another_user(self):
        self.client.force_login(self.member)

        response = self.client.post(
            reverse("accounts:profile"),
            {
                "first_name": "Test",
                "last_name": "Member",
                "email": "manager@example.com",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.member.refresh_from_db()
        self.assertEqual(self.member.email, "member@example.com")


class PasswordChangeTests(AccountTestBase):
    def test_password_change_requires_login(self):
        response = self.client.get(reverse("accounts:password-change"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:password-change')}",
        )

    def test_member_can_change_password_and_remains_logged_in(self):
        self.client.force_login(self.member)

        response = self.client.post(
            reverse("accounts:password-change"),
            {
                "old_password": "TestPass123!",
                "new_password1": "NewStrongPass456!",
                "new_password2": "NewStrongPass456!",
            },
        )

        self.assertRedirects(response, reverse("accounts:profile"))

        self.member.refresh_from_db()
        self.assertTrue(self.member.check_password("NewStrongPass456!"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_password_change_rejects_incorrect_old_password(self):
        self.client.force_login(self.member)

        response = self.client.post(
            reverse("accounts:password-change"),
            {
                "old_password": "WrongPassword!",
                "new_password1": "NewStrongPass456!",
                "new_password2": "NewStrongPass456!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.member.refresh_from_db()
        self.assertTrue(self.member.check_password("TestPass123!"))


class AdminUserManagementTests(AccountTestBase):
    def test_admin_can_view_user_list(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("accounts:admin-users"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "member@example.com")
        self.assertContains(response, "manager@example.com")

    def test_member_cannot_view_admin_user_list(self):
        self.client.force_login(self.member)

        response = self.client.get(reverse("accounts:admin-users"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_manager_cannot_view_admin_user_list(self):
        self.client.force_login(self.manager)

        response = self.client.get(reverse("accounts:admin-users"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_admin_can_change_user_role_and_activation(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("accounts:admin-user-edit", args=[self.member.pk]),
            {
                "first_name": "Test",
                "last_name": "Member",
                "email": "member@example.com",
                "role": User.Role.MANAGER,
                "is_active": "",
            },
        )

        self.assertRedirects(response, reverse("accounts:admin-users"))

        self.member.refresh_from_db()
        self.assertEqual(self.member.role, User.Role.MANAGER)
        self.assertFalse(self.member.is_active)

    def test_non_admin_cannot_edit_users(self):
        self.client.force_login(self.member)

        response = self.client.get(
            reverse("accounts:admin-user-edit", args=[self.manager.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_admin_update_form_rejects_duplicate_email(self):
        form = AdminUserUpdateForm(
            data={
                "first_name": "Test",
                "last_name": "Member",
                "email": "manager@example.com",
                "role": User.Role.MEMBER,
                "is_active": "on",
            },
            instance=self.member,
        )

        self.assertFalse(form.is_valid())


class AccountFormTests(AccountTestBase):
    def test_signup_form_rejects_duplicate_email(self):
        User.objects.create_user(
            email="existing@example.com",
            password="TestPass123!",
        )

        form = SignUpForm(
            data={
                "email": "existing@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )

        self.assertFalse(form.is_valid())

    def test_profile_form_normalizes_email(self):
        form = ProfileUpdateForm(
            data={
                "first_name": "Test",
                "last_name": "Member",
                "email": "  MEMBER@EXAMPLE.COM ",
            },
            instance=self.member,
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["email"], "member@example.com")
