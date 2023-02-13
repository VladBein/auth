from datetime import datetime

from .model import AuthUser
from .user import ModelUser
from .utils import hashing
from ..commands import CreateTokens
from src.auth_user.common.exceptions import InvalidPassword


class Authorization(AuthUser):
    def __call__(self, user: ModelUser, password: str) -> None:
        if user.password != hashing(password):
            raise InvalidPassword("Invalid password")
        self.events.append(CreateTokens(sub=user.login, iat=datetime.now()))
