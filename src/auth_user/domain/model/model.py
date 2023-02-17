from typing import List, Union

from auth_user.domain.message.commands import Command
from auth_user.domain.message.events import Event


class AuthUser:
    events: List[Union[Command, Event]]

    def __init__(self):
        self.events = []
