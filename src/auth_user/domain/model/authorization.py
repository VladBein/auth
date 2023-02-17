from datetime import datetime

from .model import AuthUser
from .user import ModelUser
from .utils import hashing
from auth_user.domain.message.commands import CreateTokens
from auth_user.common.exceptions import InvalidPassword


class Authorization(AuthUser):
    def __call__(self, user: ModelUser, password: str) -> None:
        if user.password != hashing(password):
            raise InvalidPassword(f"Invalid password {password}")
        self.events.append(CreateTokens(sub=user.login, iat=datetime.now()))
