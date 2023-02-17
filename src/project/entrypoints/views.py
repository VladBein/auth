import redis
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.viewsets import GenericViewSet

from auth_user.common.exceptions import UserAlreadyExists, InvalidPassword, RestorePasswordRequestAlreadyExists, \
    RestorePasswordRequestNotFound, RegistrationRequestNotFound, InvalidSecurityData, UserNotFound, \
    RegistrationRequestAlreadyExists, InvalidToken
from auth_user.domain import commands
from auth_user.service_layer.messagebus import handle
from auth_user.service_layer.serializers import UserWithPasswordSerializer, UUIDSerializer, EmailAndLoginSerializer, \
    UUIDAndNewPasswordSerializer, NewPasswordSerializer
from auth_user.service_layer.uow import DjangoORMAndRedisClientUnitOfWork, DjangoORMUnitOfWork

redis_client = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)


class AccountView(GenericViewSet):
    def create(self, request):
        try:
            serializer = UUIDSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            cmd = commands.Registration(uuid=serializer.validated_data["uuid"])
            uow = DjangoORMAndRedisClientUnitOfWork(redis_client)
            handle(cmd, uow)
        except (UserAlreadyExists, RegistrationRequestNotFound) as error:
            return Response(data={"message": str(error)}, status=HTTP_400_BAD_REQUEST)
        return Response(data={"message": "Registration confirmed"}, status=HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def new(self, request):
        try:
            serializer = UserWithPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            cmd = commands.RequestRegistration(**serializer.validated_data)
            uow = DjangoORMAndRedisClientUnitOfWork(redis_client)
            handle(cmd, uow)
        except (UserAlreadyExists, RegistrationRequestAlreadyExists) as error:
            return Response(data={"message": str(error)}, status=HTTP_400_BAD_REQUEST)
        return Response(data={"message": "Email sent"}, status=HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="password/restore")
    def restore_password(self, request):
        try:
            serializer = EmailAndLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            cmd = commands.RequestRestorePassword(**serializer.validated_data)
            uow = DjangoORMAndRedisClientUnitOfWork(redis_client)
            handle(cmd, uow)
        except (RestorePasswordRequestAlreadyExists, UserNotFound) as error:
            return Response({"message": str(error)}, status=HTTP_400_BAD_REQUEST)
        return Response({"message": "Email sent"}, status=HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def password(self, request):
        try:
            serializer = UUIDAndNewPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            cmd = commands.RestorePassword(**serializer.validated_data)
            uow = DjangoORMAndRedisClientUnitOfWork(redis_client)
            handle(cmd, uow)
        except RestorePasswordRequestNotFound as error:
            return Response({"message": str(error)}, status=HTTP_400_BAD_REQUEST)

        return Response({"message": "Password changed"}, status=HTTP_200_OK)

    @action(detail=False, methods=["put"], url_path="password")
    def change_password(self, request):
        try:
            serializer = NewPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            uow = DjangoORMUnitOfWork()
            security_data = commands.AuthenticateByAccessToken(security_data=request.headers["Authorization"])
            login = handle(security_data, uow).pop()
            cmd = commands.ChangePassword(
                login,
                serializer.validated_data["new_password"]
            )
            handle(cmd, uow)
        except InvalidToken as error:
            return Response({"message": str(error)}, status=HTTP_400_BAD_REQUEST)
        return Response({"message": "Password changed"}, status=HTTP_200_OK)


class SecurityTokenView(GenericViewSet):
    @action(detail=False, methods=["get", "put"])
    def token(self, request):
        if request.method == "GET":
            cmd = commands.Authorize(security_data=request.headers["Authorization"])
        else:
            cmd = commands.AuthenticateByRefreshToken(security_data=request.headers["Authorization"])
        try:
            uow = DjangoORMUnitOfWork()
            _, tokens = handle(cmd, uow)
        except (InvalidSecurityData, InvalidPassword) as error:
            return Response({"message": str(error)}, status=HTTP_401_UNAUTHORIZED)
        return Response(data=tokens, status=HTTP_200_OK)
