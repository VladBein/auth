from typing import Optional
import abc

from src.auth_user.domain.model.user import ModelUser
from src.core.models import User


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, login: str) -> Optional[ModelUser]:
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, user: ModelUser) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, user: ModelUser) -> None:
        raise NotImplementedError


class DjangoORMRepository(AbstractRepository):
    def get(self, login: str) -> Optional[ModelUser]:
        user = User.objects.filter(login=login).first()
        try:
            return ModelUser(
                first_name=user.first_name,
                last_name=user.last_name,
                patronymic=user.patronymic,
                email=user.email,
                login=user.login,
                password=user.password,
            )
        except AttributeError:
            return None

    def add(self, model_user: ModelUser) -> None:
        User.objects.create(
            first_name=model_user.first_name,
            last_name=model_user.last_name,
            patronymic=model_user.patronymic,
            email=model_user.email,
            login=model_user.login,
            password=model_user.password
        )

    def update(self, model_user: ModelUser) -> None:
        user = User.objects.filter(login=model_user.login).first()
        try:
            user.first_name = model_user.first_name
            user.last_name = model_user.last_name
            user.patronymic = model_user.patronymic
            user.email = model_user.email
            user.password = model_user.password
            user.save()
        except AttributeError:
            return None
