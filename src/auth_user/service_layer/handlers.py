from enum import Enum
from dataclasses import astuple, asdict

from auth_user.domain.model.user import ModelUser
from auth_user.domain.model.token import JWTToken
from auth_user.domain.model.authorization import Authorization
from auth_user.domain.model.authentication import AuthenticationByAccessToken, AuthenticationByRefreshToken
from auth_user.domain.model.utils import decode_base64
from auth_user.domain import commands
from auth_user.domain import events
from .serializers import UserSerializer
from .uow import UnitOfWork, DjangoORMUnitOfWork, DjangoORMAndRedisClientUnitOfWork
from auth_user.common.exceptions import UserAlreadyExists, RegistrationRequestAlreadyExists, \
    RegistrationRequestNotFound, InvalidSecurityData, RestorePasswordRequestAlreadyExists, \
    RestorePasswordRequestNotFound, UserNotFound
from auth_user.adapters import email


class RedisStatus(Enum):
    REGISTRATION = 0
    PASSWORD_RESTORE = 1


def make_registration_request(cmd: commands.RequestRegistration, uow: DjangoORMAndRedisClientUnitOfWork) -> None:
    user = ModelUser(*astuple(cmd))
    with uow:
        pattern = f"{RedisStatus.REGISTRATION.value} * {user.login} *"
        if uow.users.get(user.login) or uow.redis_client.keys(pattern):
            raise UserAlreadyExists("User already exists")

        pattern = f"{RedisStatus.REGISTRATION.value} {user.email} *"
        if uow.redis_client.keys(pattern):
            raise RegistrationRequestAlreadyExists("Registration request already exists")

        name = f"{RedisStatus.REGISTRATION.value} {user.email} {user.login} {user.uuid}"
        uow.redis_client.hset(name, mapping={key: value for key, value in asdict(user).items() if key != "new"})
        uow.redis_client.expire(name, time=3600)  # ToDo: потом перенесем в настройки

        event = events.Registration(user.email, user.uuid)
        uow.events.append(event)


def add_user(cmd: commands.Registration, uow: DjangoORMAndRedisClientUnitOfWork) -> dict:
    with uow:
        pattern = f"* {cmd.uuid}"
        available_keys = uow.redis_client.keys(pattern)
        if not available_keys:
            raise RegistrationRequestNotFound("Registration request not found")

        data = uow.redis_client.hgetall(available_keys[0])
        user = ModelUser(
            data["first_name"],
            data["last_name"],
            data["patronymic"],
            data["email"],
            data["login"],
            data["password"],
            new=True
        )
        uow.users.add(user)

        serializer = UserSerializer(user)
        return serializer.data


def create_tokens(cmd: commands.CreateTokens, uow: UnitOfWork) -> dict:
    return JWTToken.create_access_and_refresh_tokens(cmd.sub, cmd.iat)


def authorize_user(cmd: commands.Authorize, uow: DjangoORMUnitOfWork) -> None:
    try:
        login, password = decode_base64(cmd.security_data).split(":")
    except Exception:
        raise InvalidSecurityData("Invalid security data")

    with uow:
        user = uow.users.get(login)
        if not user:
            raise InvalidSecurityData("Invalid security data")

        auth = Authorization()
        auth(user, password)
        uow & auth


def authenticate_user_by_access_token(cmd: commands.AuthenticateByAccessToken, uow: UnitOfWork) -> str:
    auth = AuthenticationByAccessToken()
    return auth(cmd.security_data)


def authenticate_user_by_refresh_token(cmd: commands.AuthenticateByRefreshToken, uow: UnitOfWork) -> None:
    auth = AuthenticationByRefreshToken()
    auth(cmd.security_data)
    uow & auth


def change_password(cmd: commands.ChangePassword, uow: DjangoORMUnitOfWork) -> None:
    with uow:
        user = uow.users.get(cmd.login)
        user.change_password(cmd.new_password)
        uow.users.update(user)


def make_restore_password_request(
        cmd: commands.RequestRestorePassword,
        uow: DjangoORMAndRedisClientUnitOfWork) -> None:
    with uow:
        user = uow.users.get(cmd.login)
        if not user or user.email != cmd.email:
            raise UserNotFound("User not found")

        pattern = f"{RedisStatus.PASSWORD_RESTORE.value} {user.uuid}"
        if uow.redis_client.keys(pattern):
            raise RestorePasswordRequestAlreadyExists("Restore password request already exists")

        name = pattern
        uow.redis_client.set(name, user.login)
        uow.redis_client.expire(name, time=3600)  # ToDo: потом перенесем в настройки

        event = events.RestorePassword(user.email, user.uuid)
        uow.events.append(event)


def restore_password(cmd: commands.RestorePassword, uow: DjangoORMAndRedisClientUnitOfWork) -> None:
    with uow:
        name = f"{RedisStatus.PASSWORD_RESTORE.value} {cmd.uuid}"
        value = uow.redis_client.get(name)
        if not value:
            raise RestorePasswordRequestNotFound("Restore password request not found")

        cmd = commands.ChangePassword(login=value, new_password=cmd.new_password)
        uow.events.append(cmd)


def send_registration_confirmation(event: events.Registration, uow: UnitOfWork) -> None:
    email.send(event.email, "Регистрация", event.uuid)


def send_restore_password_confirmation(event: events.RestorePassword, uow: UnitOfWork) -> None:
    email.send(event.email, "Восстановление пароля", event.uuid)
