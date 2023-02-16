from datetime import datetime

from django.test import TestCase

from auth_user.domain.model.token import JWTToken
from auth_user.common.exceptions import InvalidSecurityData


class TokenTestCase(TestCase):
    def test_creating_access_and_refresh_tokens(self):
        tokens = JWTToken.create_access_and_refresh_tokens(
            sub="login1",
            iat=datetime.now(),
        )

        self.assertIsInstance(tokens, dict)
        self.assertIn("access", tokens)
        self.assertIsInstance(tokens["access"], str)
        self.assertIn("refresh", tokens)
        self.assertIsInstance(tokens["refresh"], str)

    def test_getting_token_from_security_data(self):
        initial_token = JWTToken(
            sub="login1",
            iat=datetime.now().replace(microsecond=0),
            exp=30,
        )
        security_data = str(initial_token)

        token = JWTToken.get_token_from_security_data(security_data)

        self.assertEqual(token.sub, initial_token.sub)
        self.assertEqual(token.iat, initial_token.iat)
        self.assertEqual(token.exp, initial_token.exp)

    def test_error_getting_token_from_security_data(self):
        self.assertRaises(
            InvalidSecurityData,
            JWTToken.get_token_from_security_data,
            "test"
        )
        self.assertRaises(
            InvalidSecurityData,
            JWTToken.get_token_from_security_data,
            "test.test.test"
        )
