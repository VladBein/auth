from datetime import datetime, timedelta

from .model import AuthUser
from .token import JWTToken
from ..commands import CreateTokens
from src.auth_user.common.exceptions import InvalidToken


Login = str


class Authentication:
    def __call__(self, security_data: str) -> Login:
        token = JWTToken.get_token_from_security_data(security_data)
        if token.iat + timedelta(token.exp) > datetime.now():
            raise InvalidToken
        return token.sub


class AuthenticationByAccessToken(Authentication):
    ...


class AuthenticationByRefreshToken(AuthUser, Authentication):
    def __call__(self, security_data: str) -> Login:
        login = super().__call__(security_data)
        self.events.append(CreateTokens(sub=login, iat=datetime.now()))
        return login
