from datetime import datetime

from django.test import TestCase

from auth_user.domain.model.authentication import Authentication
from auth_user.domain.model.token import JWTToken
from auth_user.common.exceptions import InvalidToken


class AuthenticationTestCase(TestCase):
    def test_success_authentication(self):
        token = JWTToken(
            sub="login1",
            iat=datetime.now(),
            exp=30,
        )
        security_data = str(token)

        auth = Authentication()
        login = auth(security_data)

        self.assertEqual(login, "login1")

    def test_fail_authentication(self):
        token = JWTToken(
            sub="login1",
            iat=datetime.now(),
            exp=0,
        )
        security_data = str(token)

        with self.assertRaises(InvalidToken):
            auth = Authentication()
            auth(security_data)
