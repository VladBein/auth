from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from auth_user.adapters.repository import DjangoORMRepository
from auth_user.domain.model.user import ModelUser
from auth_user.domain.model.utils import encode_base64, hashing


class RegistrationTestCase(APITestCase):
    def test_registration(self):
        client = {
            'first_name': 'firstname1',
            'last_name': 'lastname1',
            'patronymic': 'patronymic1',
            'email': 'email2@mail.ru',
            'login': 'login2',
            'password': 'password1',
        }
        response = self.client.post('/api/v1/account/new/', data=client)
        response_data = response.json()
        print(response_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        uuid = {'uuid': 'dd107184-6f5a-37b1-b54b-517cfd8053ad'}
        response = self.client.post('/api/v1/account/', data=uuid)
        response_data = response.json()
        print(response_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authorisation(self):
        model_user = ModelUser(
            first_name='firstname1',
            last_name='lastname1',
            patronymic='patronymic1',
            email='email1',
            login='login1',
            password=hashing('password1')
        )
        repository = DjangoORMRepository()
        repository.add(model_user)

        data_base64 = encode_base64('login1:password1')

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=data_base64)
        response = client.get('/api/v1/security/token/')
        response_data = response.json()
        print(response_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)





