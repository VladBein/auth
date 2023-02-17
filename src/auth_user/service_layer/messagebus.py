import logging
from typing import List, Dict, Callable, Type, Union

from auth_user.domain.message import commands, events
from auth_user.service_layer import handlers
from auth_user.service_layer.uow import UnitOfWork


logger = logging.getLogger(__name__)


EVENT_HANDLERS = {
    events.Registration: [handlers.send_registration_confirmation],
    events.RestorePassword: [handlers.send_restore_password_confirmation],
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.RequestRegistration: handlers.make_registration_request,
    commands.Registration: handlers.add_user,
    commands.CreateTokens: handlers.create_tokens,
    commands.Authorize: handlers.authorize_user,
    commands.AuthenticateByAccessToken: handlers.authenticate_user_by_access_token,
    commands.AuthenticateByRefreshToken: handlers.authenticate_user_by_refresh_token,
    commands.ChangePassword: handlers.change_password,
    commands.RequestRestorePassword: handlers.make_restore_password_request,
    commands.RestorePassword: handlers.restore_password,
}  # type: Dict[Type[commands.Command], Callable]


Message = Union[commands.Command, events.Event]


def handle_event(event: events.Event, queue: List[Message], uow: UnitOfWork):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            logger.debug("handling event %s with handler %s", event, handler)
            handler(event, uow=uow)
            queue.extend(uow.collect_new_events())
        except Exception:
            logger.exception("Exception handling event %s", event)
            continue


def handle_command(command: commands.Command, queue: List[Message], uow: UnitOfWork):
    logger.debug("handling command %s", command)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow=uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        logger.exception("Exception handling command %s", command)
        raise


def handle(message: Message, uow: UnitOfWork):
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            cmd_result = handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
            raise Exception(f"{message} was not an Event or Command")
    return results
