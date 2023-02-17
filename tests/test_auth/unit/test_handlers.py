from typing import Dict, Union, List, Optional
from datetime import datetime
import re
from unittest import mock

from django.test import TestCase

from auth_user.domain.model.user import ModelUser
from auth_user.domain.model.token import JWTToken
from auth_user.domain.model.utils import encode_base64, hashing
from auth_user.adapters.repository import AbstractRepository
from auth_user.service_layer.uow import UnitOfWork
from auth_user.domain import commands
from auth_user.service_layer.messagebus import handle
from auth_user.common.exceptions import UserAlreadyExists, RegistrationRequestAlreadyExists, \
    RegistrationRequestNotFound, InvalidSecurityData, UserNotFound, RestorePasswordRequestAlreadyExists, \
    RestorePasswordRequestNotFound


class FakeRepository(AbstractRepository):
    def __init__(self, users):
        self._users = set(users)

    def get(self, login: str):
        try:
            return next(_user for _user in self._users if _user.login == login)
        except StopIteration:
            return None

    def add(self, user):
        self._users.add(user)

    def update(self, user):
        try:
            _user = next(_user for _user in self._users if _user.login == user.login)
            _user.first_name = user.first_name
            _user.last_name = user.last_name
            _user.patronymic = user.patronymic
            _user.email = user.email
            _user.password = user.password
        except StopIteration:
            return


class FakeRedisClient:
    def __init__(self, data):
        self._data = data  # type: Dict[str, Union[str, dict]]

    def keys(self, pattern: str) -> List[str]:
        pattern = pattern.replace("*", ".*")
        return [key for key in self._data.keys() if re.match(pattern, key) is not None]

    def expire(self, *args, **kwargs) -> None:
        pass

    def set(self, name: str, value: str) -> None:
        self._data[name] = value

    def get(self, name: str) -> Optional[str]:
        return self._data.get(name)

    def hset(self, name: str, mapping: dict) -> None:
        self._data[name] = mapping

    def hgetall(self, name: str) -> dict:
        return self._data[name]


class FakeUnitOfWork(UnitOfWork):
    def __init__(self, repository=None, redis_client=None):
        super().__init__()
        self.users = repository or FakeRepository([])
        self.redis_client = redis_client or FakeRedisClient({})


USER_MAPPER = {
    "first_name": "firstname1",
    "last_name": "lastname1",
    "patronymic": "patronymic1",
    "email": "email1",
    "login": "login1",
    "password": "password1",
}


class RequestRegistrationTestCase(TestCase):
    _cmd = commands.RequestRegistration(**USER_MAPPER)

    def test_success_registration_request(self):
        with mock.patch("auth_user.adapters.email.send") as mock_send_mail:
            uow = FakeUnitOfWork()
            handle(self._cmd, uow)
            self.assertEqual(
                mock_send_mail.call_args,
                mock.call("email1", "Регистрация", "21f08d25-e3e3-324a-91f7-d4a58a31c63e")
            )

    def test_fail_registration_request_because_user_exists_in_repository(self):
        user = ModelUser(**USER_MAPPER)
        uow = FakeUnitOfWork(repository=FakeRepository([user]))
        self.assertRaises(UserAlreadyExists, handle, self._cmd, uow)

    def test_fail_registration_request_because_request_exists_in_redis(self):
        user = ModelUser(**USER_MAPPER)
        key = f"0 {user.email} login2 uuid-test"
        uow = FakeUnitOfWork(redis_client=FakeRedisClient({key: USER_MAPPER}))
        self.assertRaises(RegistrationRequestAlreadyExists, handle, self._cmd, uow)


class RegistrationTestCase(TestCase):
    _cmd = commands.Registration(ModelUser(**USER_MAPPER).uuid)

    def test_success_registration(self):
        user = ModelUser(**USER_MAPPER)
        key = f"0 {user.email} {user.login} {user.uuid}"
        uow = FakeUnitOfWork(redis_client=FakeRedisClient({key: USER_MAPPER}))

        results = handle(self._cmd, uow)

        self.assertIsNotNone(uow.users.get("login1"))
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], dict)
        self.assertDictEqual(
            results[0],
            {key: value for key, value in USER_MAPPER.items() if key != "password"}
        )

    def test_fail_registration_because_request_not_in_redis(self):
        uow = FakeUnitOfWork()
        self.assertRaises(RegistrationRequestNotFound, handle, self._cmd, uow)


class AuthorizationTestCase(TestCase):
    def setUp(self):
        self._cmd = commands.Authorize(security_data=encode_base64("login1:password1"))

    def test_success_authorization(self):
        user = ModelUser(**USER_MAPPER, new=True)
        uow = FakeUnitOfWork(repository=FakeRepository([user]))

        results = handle(self._cmd, uow)

        self.assertEqual(len(results), 2)
        self.assertIsNone(results[0])
        self.assertIsInstance(results[1], dict)

    def test_fail_authorization_because_user_not_in_repository(self):
        uow = FakeUnitOfWork()
        self.assertRaises(InvalidSecurityData, handle, self._cmd, uow)

    def test_fail_authorization_because_invalid_security_data(self):
        self._cmd.security_data = "test"
        uow = FakeUnitOfWork()
        self.assertRaises(InvalidSecurityData, handle, self._cmd, uow)


class AuthenticationTestCase(TestCase):
    _security_data = str(JWTToken(sub="login1", iat=datetime.now(), exp=30))

    def test_success_authentication_by_access_token(self):
        cmd = commands.AuthenticateByAccessToken(self._security_data)
        uow = FakeUnitOfWork()

        results = handle(cmd, uow)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], "login1")

    def test_success_authentication_by_refresh_token(self):
        cmd = commands.AuthenticateByRefreshToken(self._security_data)
        uow = FakeUnitOfWork()

        results = handle(cmd, uow)

        self.assertEqual(len(results), 2)
        self.assertIsNone(results[0])
        self.assertIsInstance(results[1], dict)


class RequestRestorePasswordTestCase(TestCase):
    def setUp(self):
        self._cmd = commands.RequestRestorePassword(email="email1", login="login1")

    def test_success_restore_password_request(self):
        with mock.patch("auth_user.adapters.email.send") as mock_send_mail:
            user = ModelUser(**USER_MAPPER)
            uow = FakeUnitOfWork(repository=FakeRepository([user]))
            handle(self._cmd, uow)
            self.assertEqual(
                mock_send_mail.call_args,
                mock.call("email1", "Восстановление пароля", user.uuid)
            )

    def test_fail_restore_password_request_because_user_not_in_repository(self):
        uow = FakeUnitOfWork()
        self.assertRaises(UserNotFound, handle, self._cmd, uow)

    def test_fail_restore_password_request_because_invalid_email(self):
        self._cmd.email = "email2"
        uow = FakeUnitOfWork()
        self.assertRaises(UserNotFound, handle, self._cmd, uow)

    def test_fail_restore_password_request_because_request_exists_in_redis(self):
        user = ModelUser(**USER_MAPPER)
        key = f"1 {user.uuid}"
        uow = FakeUnitOfWork(
            repository=FakeRepository([user]),
            redis_client=FakeRedisClient({key: USER_MAPPER})
        )
        self.assertRaises(RestorePasswordRequestAlreadyExists, handle, self._cmd, uow)


class RestorePasswordTestCase(TestCase):
    _user = ModelUser(**USER_MAPPER)
    _cmd = commands.RestorePassword(_user.uuid, "new-password")

    def test_success_restore_password(self):
        key = f"1 {self._user.uuid}"
        uow = FakeUnitOfWork(
            repository=FakeRepository([self._user]),
            redis_client=FakeRedisClient({key: self._user.login})
        )

        handle(self._cmd, uow)

        self.assertEqual(uow.users.get(self._user.login).password, hashing("new-password"))

    def test_fail_restore_password_because_request_not_in_redis(self):
        uow = FakeUnitOfWork()
        self.assertRaises(RestorePasswordRequestNotFound, handle, self._cmd, uow)
