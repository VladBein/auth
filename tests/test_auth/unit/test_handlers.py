from typing import Dict, Union, List
import re
from unittest import mock

from django.test import TestCase

from auth_user.adapters.repository import AbstractRepository
from auth_user.service_layer.uow import UnitOfWork
from auth_user.service_layer.messagebus import handle
from auth_user.domain import commands
from auth_user.domain import events
from auth_user.domain.model.user import ModelUser
from auth_user.domain.model.utils import encode_base64


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

    def get(self, name: str) -> str:
        return self._data[name]

    def hset(self, name: str, mapping: dict) -> None:
        self._data[name] = mapping

    def hgetall(self, name: str) -> dict:
        return self._data[name]


class FakeUnitOfWork(UnitOfWork):
    def __init__(self, redis_client=FakeRedisClient({}), repository=FakeRepository([])):
        super().__init__()
        self.redis_client = redis_client
        self.users = repository


USER_MAPPER = {
    "first_name": "firstname1",
    "last_name": "lastname1",
    "patronymic": "patronymic1",
    "email": "email1",
    "login": "login1",
    "password": "password1",
}


class RegistrationTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cmd = commands.RequestRegistration(**USER_MAPPER)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_success_registration_request(self):
        with mock.patch("auth_user.adapters.email.send") as mock_send_mail:
            uow = FakeUnitOfWork()
            handle(self.cmd, uow)
            self.assertEqual(
                mock_send_mail.call_args,
                mock.call("email1", "Регистрация", "21f08d25-e3e3-324a-91f7-d4a58a31c63e")
            )

    def test_fail_registration_request(self):
        ...


class AuthorizationTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cmd = commands.Authorize(security_data=encode_base64("login1:password1"))

    @classmethod
    def tearDownClass(cls):
        pass

    def test_success_authorization(self):
        user = ModelUser(**USER_MAPPER, new=True)
        uow = FakeUnitOfWork(repository=FakeRepository([user]))

        results = handle(self.cmd, uow)

        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[1], dict)
        self.assertIn("access", results[1])
        self.assertIn("refresh", results[1])
