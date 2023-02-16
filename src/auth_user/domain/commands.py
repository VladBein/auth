from dataclasses import dataclass
from datetime import datetime


class Command:
    ...


@dataclass
class RequestRegistration(Command):
    first_name: str
    last_name: str
    patronymic: str
    email: str
    login: str
    password: str


@dataclass
class Registration(Command):
    uuid: str


@dataclass
class CreateTokens(Command):
    sub: str
    iat: datetime


@dataclass
class Authorize(Command):
    security_data: str


@dataclass
class AuthenticateByAccessToken(Command):
    security_data: str


@dataclass
class AuthenticateByRefreshToken(Command):
    security_data: str


@dataclass
class ChangePassword(Command):
    login: str
    new_password: str


@dataclass
class RequestRestorePassword(Command):
    email: str
    login: str


@dataclass
class RestorePassword(Command):
    uuid: str
    new_password: str
