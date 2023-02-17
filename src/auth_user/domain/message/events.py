from dataclasses import dataclass


class Event:
    ...


@dataclass
class Registration(Event):
    email: str
    uuid: str


@dataclass
class RestorePassword(Event):
    email: str
    uuid: str
