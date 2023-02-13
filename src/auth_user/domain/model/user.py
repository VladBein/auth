from dataclasses import dataclass
import uuid

from .utils import hashing


@dataclass(unsafe_hash=True)
class ModelUser:
    first_name: str
    last_name: str
    patronymic: str
    email: str
    login: str
    password: str
    new: bool = False

    def __post_init__(self) -> None:
        if self.new:
            self.password = hashing(self.password)

    @property
    def uuid(self) -> str:
        return str(uuid.uuid3(uuid.NAMESPACE_URL, name=self.login))

    def change_password(self, new_password: str) -> None:
        self.password = hashing(new_password)
