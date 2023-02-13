from django.test import TestCase

from auth_user.domain.model.auth import ModelUser, Authorization, JWTToken


class AuthorizationTestCase(TestCase):
    def test_authorization_getting_jwt_token(self):
        user = ModelUser(
            first_name="firstname1",
            last_name="lastname1",
            patronymic="patronymic1",
            email="email1",
            login="login1",
            password="hash1"
        )

        auth = Authorization(user, 'hash1')
        jwt_token = auth.get_access_token()
        self.assertIsInstance(jwt_token, JWTToken)

    def test_authentication_on_jwt_token(self):
        token = 'ZXlkaGJHY25PaUFuU0ZNeU5UWW5MQ0FuZEhsd0p6b2dKMHBYVkNkOS5leWR6ZFdJbk9pQW5iRzluYVc0eEp5d2dKMmxoZENjNklDY3lNREl6TFRBeUxUQXhJREE1T2pRek9qUXpMakUzTURZeE5DZDkuOGU0MmM5ZGVkNDM4YmM1YWY5ZTFlYTc5OWE3ZWNmZjgyODg3NTE0MTZkZDYyYmZlY2UxYTliOWQ1YmRlNzc2OQ=='

        jwt_token = JWTToken.get_jwt_token(token)
        self.assertDictEqual(
            jwt_token._header,
            {
                'alg': 'HS256',
                'typ': 'JWT'
            }
        )
        self.assertDictEqual(
            jwt_token._payload,
            {
                'sub': 'login1',
                'iat': '2023-02-01 09:43:43.170614'
            }
        )
