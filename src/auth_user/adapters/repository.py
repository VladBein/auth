import abc

from auth_user.domain.model.user import ModelUser
from project.core.models import User


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, login: str) -> ModelUser | None:
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, user: ModelUser) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, user: ModelUser) -> None:
        raise NotImplementedError


class DjangoORMRepository(AbstractRepository):
    def get(self, login):
        instance_user = User.objects.filter(login=login).first()
        try:
            return ModelUser(
                first_name=instance_user.first_name,
                last_name=instance_user.last_name,
                patronymic=instance_user.patronymic,
                email=instance_user.email,
                login=instance_user.login,
                password=instance_user.password,
            )
        except AttributeError:
            return None

    def add(self, user):
        User.objects.create(
            first_name=user.first_name,
            last_name=user.last_name,
            patronymic=user.patronymic,
            email=user.email,
            login=user.login,
            password=user.password
        )

    def update(self, user):
        instance_user = User.objects.filter(login=user.login).first()
        try:
            instance_user.first_name = user.first_name
            instance_user.last_name = user.last_name
            instance_user.patronymic = user.patronymic
            instance_user.email = user.email
            instance_user.password = user.password
            instance_user.save()
        except AttributeError:
            return None
