from __future__ import annotations
from typing import List, Union

from redis import Redis

from src.auth_user.adapters.repository import AbstractRepository, DjangoORMRepository
from auth_user.domain.commands import Command
from auth_user.domain.events import Event
from src.auth_user.domain.model.model import AuthUser


class UnitOfWork:
    users: AbstractRepository
    events: List[Union[Command, Event]]

    def __init__(self):
        self.events = []

    def __and__(self, other: AuthUser) -> None:
        self.events.extend(other.events)

    # ToDo: контекстный менеджер более гибкая модель (можем легко перейти на голый SQL или NoSql DB)
    def __enter__(self) -> UnitOfWork:
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def collect_new_events(self):
        while self.events:
            yield self.events.pop(0)


class DjangoORMUnitOfWork(UnitOfWork):
    def __enter__(self):
        self.users = DjangoORMRepository()
        return super().__enter__()


class DjangoORMAndRedisClientUnitOfWork(DjangoORMUnitOfWork):
    redis_client: Redis

    def __init__(self, redis_client):
        super().__init__()
        self.redis_client = redis_client

    def __exit__(self, *args, **kwargs):
        super().__exit__(*args, **kwargs)
        self.redis_client.close()
