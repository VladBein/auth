from django.test import TestCase

from src.auth_user.adapters.repository import DjangoORMRepository
from src.auth_user.domain.model.user import ModelUser

from project.core.models import User


class RepositoryTestCase(TestCase):
    def test_get_model_user(self):
        User.objects.create(
            first_name='firstname1',
            last_name='lastname1',
            patronymic='patronymic1',
            email='email1',
            login='login1',
            password='password1'
        )
        repository = DjangoORMRepository()
        user = repository.get(login='login1')
        self.assertIsInstance(user, ModelUser)
        self.assertEqual(user.first_name, 'firstname1')
        self.assertEqual(user.last_name, 'lastname1')
        self.assertEqual(user.patronymic, 'patronymic1')
        self.assertEqual(user.email, 'email1')
        self.assertEqual(user.login, 'login1')
        self.assertEqual(user.password, 'password1')

    def test_add_model_user(self):
        model_user = ModelUser(
            first_name='firstname1',
            last_name='lastname1',
            patronymic='patronymic1',
            email='email1',
            login='login1',
            password='password1'
        )
        repository = DjangoORMRepository()
        repository.add(model_user)
        self.assertEqual(User.objects.filter(login=model_user.login).count(), 1)

    def test_update_user(self):
        User.objects.create(
            first_name='firstname1',
            last_name='lastname1',
            patronymic='patronymic1',
            email='email1',
            login='login1',
            password='password1'
        )
        model_user = ModelUser(
            first_name='firstname2',
            last_name='lastname2',
            patronymic='patronymic2',
            email='email2',
            login='login1',
            password='password2'
        )
        repository = DjangoORMRepository()
        repository.update(model_user)
        user = User.objects.filter(login=model_user.login).first()

        self.assertEqual(user.first_name, model_user.first_name)
        self.assertEqual(user.last_name, model_user.last_name)
        self.assertEqual(user.patronymic, model_user.patronymic)
        self.assertEqual(user.email, model_user.email)
        self.assertEqual(user.login, model_user.login)
        self.assertEqual(user.password, model_user.password)
