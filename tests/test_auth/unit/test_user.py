from django.test import TestCase

from auth_user.domain.model.user import ModelUser


class UserTestCase(TestCase):
    def setUp(self):
        self._user = ModelUser(
            first_name='firstname1',
            last_name='lastname1',
            patronymic='patronymic1',
            email='email1',
            login='login1',
            password='password1',
            new=True,
        )

    def test_when_creating_new_user_password_is_hashed(self):
        self.assertNotEqual(self._user.password, "password1")

    def test_user_has_uuid(self):
        self.assertIsInstance(self._user.uuid, str)

    def test_changing_password(self):
        current_password = self._user.password

        self._user.change_password("new-password1")

        self.assertNotEqual(self._user.password, current_password)
        self.assertNotEqual(self._user.password, "new-password1")
