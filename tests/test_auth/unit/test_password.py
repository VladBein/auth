from django.test import TestCase

from src.auth_user.domain.model.auth import Password


class PasswordCaseTest(TestCase):
    def test_hash_password(self):
        password_hash = Password('password1')
        self.assertNotEqual(password_hash, 'password1')
