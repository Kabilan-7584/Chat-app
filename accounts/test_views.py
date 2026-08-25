from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AuthenticationViewTests(TestCase):

    def test_signup_page_loads(self):
        response = self.client.get(
            reverse("accounts:signup")
        )

        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get(
            reverse("accounts:login")
        )

        self.assertEqual(response.status_code, 200)

    def test_protected_page_redirects_when_logged_out(self):
        response = self.client.get(
            reverse("accounts:protected")
        )

        self.assertEqual(response.status_code, 302)

    def test_protected_page_accessible_when_logged_in(self):
        User.objects.create_user(
            username="testuser",
            password="StrongPassword123!",
        )

        self.client.login(
            username="testuser",
            password="StrongPassword123!",
        )

        response = self.client.get(
            reverse("accounts:protected")
        )

        self.assertEqual(response.status_code, 200)