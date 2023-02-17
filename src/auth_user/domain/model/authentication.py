from datetime import datetime, timedelta

from .model import AuthUser
from .token import JWTToken
from auth_user.domain.message.commands import CreateTokens
from auth_user.common.exceptions import InvalidToken


Login = str


class Authentication:
    def __call__(self, security_data: str) -> Login:
        token = JWTToken.get_token_from_security_data(security_data)
        if datetime.now() > token.iat + timedelta(minutes=token.exp):
            raise InvalidToken(f"Invalid token {security_data}")
        return token.sub


class AuthenticationByAccessToken(Authentication):
    ...


class AuthenticationByRefreshToken(AuthUser, Authentication):
    def __call__(self, security_data: str) -> None:
        login = super().__call__(security_data)
        self.events.append(CreateTokens(sub=login, iat=datetime.now()))
