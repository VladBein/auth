class UserAlreadyExists(Exception):
    pass


class RegistrationRequestAlreadyExists(Exception):
    pass


class RegistrationRequestNotFound(Exception):
    pass


class UserNotFound(Exception):
    pass


class InvalidSecurityData(Exception):
    pass


class InvalidPassword(Exception):
    pass


class InvalidToken(Exception):
    pass


class RestorePasswordRequestAlreadyExists(Exception):
    pass


class RestorePasswordRequestNotFound(Exception):
    pass
