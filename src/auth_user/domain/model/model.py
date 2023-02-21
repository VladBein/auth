from auth_user.domain.message.commands import Command
from auth_user.domain.message.events import Event


class AuthUser:
    events: list[Command | Event]

    def __init__(self):
        self.events = []
