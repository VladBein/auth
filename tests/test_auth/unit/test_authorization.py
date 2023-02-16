from django.test import TestCase

from auth_user.domain.model.user import ModelUser
from auth_user.domain.model.authorization import Authorization
from auth_user.common.exceptions import InvalidPassword


class AuthorizationTestCase(TestCase):
    def test_success_authorization(self):
        user = ModelUser(
            first_name="firstname1",
            last_name="lastname1",
            patronymic="patronymic1",
            email="email1",
            login="login1",
            password="password1",
            new=True,
        )

        auth = Authorization()
        auth(user, "password1")

        self.assertEqual(len(auth.events), 1)

    def test_fail_authorization(self):
        user = ModelUser(
            first_name="firstname1",
            last_name="lastname1",
            patronymic="patronymic1",
            email="email1",
            login="login1",
            password="password1",
            new=True,
        )

        with self.assertRaises(InvalidPassword):
            auth = Authorization()
            auth(user, "password2")
