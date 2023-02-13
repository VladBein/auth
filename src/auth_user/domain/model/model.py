from typing import List, Union

from ..commands import Command
from ..events import Event


class AuthUser:
    events: List[Union[Command, Event]]

    def __init__(self):
        self.events = []
