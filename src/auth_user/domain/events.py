from dataclasses import dataclass


class Event:
    ...


@dataclass
class SendMessage(Event):
    to: str
    subject: str
    msg: str
