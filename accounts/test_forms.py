from django.test import TestCase

from accounts.forms import SignupForm


class SignupFormTests(TestCase):

    def test_valid_signup_form(self):
        form = SignupForm(
            data={
                "username": "testuser",
                "password1": "StrongPassword123!",
                "password2": "StrongPassword123!",
            }
        )

        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        form = SignupForm(
            data={
                "username": "testuser",
                "password1": "StrongPassword123!",
                "password2": "DifferentPassword123!",
            }
        )

        self.assertFalse(form.is_valid())