from dataclasses import asdict

from django.test import TestCase

from auth_user.domain.model.user import ModelUser
from auth_user.service_layer.uow import DjangoORMUnitOfWork
from project.core.models import User


# ToDo: тестировать redis необходимо в контейнере
class DjangoORMUnitOfWorkTestCase(TestCase):
    def setUp(self):
        self._user_mapper = dict(
            first_name="firstname1",
            last_name="lastname1",
            patronymic="patronymic1",
            email="email1",
            login="login1",
            password="hashed-password1",
        )

    def test_uow_can_retrieve_a_user(self):
        self._insert_user()

        with DjangoORMUnitOfWork() as uow:
            user = uow.users.get("login1")

        self._user_mapper["new"] = False
        self.assertDictEqual(asdict(user), self._user_mapper)

    def test_uow_can_add_a_user(self):
        user = self._get_model_user()

        with DjangoORMUnitOfWork() as uow:
            uow.users.add(user)

        self.assertEqual(User.objects.filter(login=user.login).count(), 1)

    def test_uow_can_update_a_user(self):
        self._insert_user()
        user = self._get_model_user()

        with DjangoORMUnitOfWork() as uow:
            uow.users.update(user)

        instance_user = User.objects.filter(login=user.login).first()
        self.assertEqual(instance_user.password, user.password)

    def _insert_user(self):
        User.objects.create(**self._user_mapper)

    def _get_model_user(self):
        self._user_mapper["password"] = "hashed-password2"
        return ModelUser(**self._user_mapper)
