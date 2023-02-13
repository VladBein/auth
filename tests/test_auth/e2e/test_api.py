from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from src.auth_user.adapters.repository import DjangoORMRepository
from src.core.models import User
from src.auth_user.domain.model.auth import ModelUser, encode_base64, Password


class ViewTestCase(APITestCase):
    def test_registration(self):
        data = {
            'first_name': 'firstname1',
            'last_name': 'lastname1',
            'patronymic': 'patronymic1',
            'email': 'email1@mail.ru',
            'login': 'login1',
            'password': 'password1',
        }
        response = self.client.post('/api/v1/account/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get().login, 'login1')

    def test_authorisation(self):
        model_user = ModelUser(
            first_name='firstname1',
            last_name='lastname1',
            patronymic='patronymic1',
            email='email1',
            login='login1',
            password=Password('password1')
        )
        repository = DjangoORMRepository()
        repository.add(model_user)

        data_base64 = encode_base64('login1:password1')

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=data_base64)
        response = client.get('/api/v1/security/token/')
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)





