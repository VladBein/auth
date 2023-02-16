import redis
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, \
    HTTP_204_NO_CONTENT

from auth_user.common.exceptions import UserAlreadyExists, InvalidPassword, RestorePasswordRequestAlreadyExists, \
    RestorePasswordRequestNotFound, RegistrationRequestNotFound, InvalidSecurityData, UserNotFound
from auth_user.domain import commands
from auth_user.service_layer import messagebus
from auth_user.service_layer.serializers import RequestRegistrationSerializer, ConfirmRegistrationSerializer, \
    RequestRestorePasswordSerializer, RestorePasswordSerializer, ChangePasswordSerializer
from auth_user.service_layer.uow import DjangoORMAndRedisClientUnitOfWork, DjangoORMUnitOfWork

redis_client = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)


def authenticate(request, uow):
    cm = commands.AuthenticateByAccessToken(
        security_data=request.headers["Authorization"]
    )
    return messagebus.handle(cm, uow)


class RequestRegistrationView(APIView):
    def post(self, request):
        try:
            serializer = RequestRegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            cmd = commands.RequestRegistration(
                serializer.validated_data["first_name"],
                serializer.validated_data["last_name"],
                serializer.validated_data["patronymic"],
                serializer.validated_data["email"],
                serializer.validated_data["login"],
                serializer.validated_data["password"]
            )
            uow = DjangoORMAndRedisClientUnitOfWork(redis_client)
            messagebus.handle(cmd, uow)
        except UserAlreadyExists as msg:
            return Response({"message": str(msg)}, status=HTTP_400_BAD_REQUEST)

        return Response({"message": "Email sent"}, status=HTTP_200_OK)


class ConfirmRegistrationView(APIView):
    def post(self, request):
        try:
            serializer = ConfirmRegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            cmd = commands.ConfirmRegistration(serializer.validated_data["uuid"])
            uow = DjangoORMAndRedisClientUnitOfWork(redis_client)
            messagebus.handle(cmd, uow)
        except (RegistrationRequestNotFound, UserAlreadyExists) as msg:
            return Response({"message": str(msg)}, status=HTTP_400_BAD_REQUEST)

        return Response({"message": "Registration confirmed"}, status=HTTP_201_CREATED)


class SecurityTokenView (APIView):
    def get(self, request):
        try:
            cmd = commands.Authorize(request.headers["Authorization"])
            uow = DjangoORMUnitOfWork()
            result = messagebus.handle(cmd, uow)
        except (InvalidPassword, InvalidSecurityData) as msg:
            return Response({"message": str(msg)}, status=HTTP_401_UNAUTHORIZED)

        return Response(data=result, status=HTTP_200_OK)

    def put(self, request):
        try:
            cm = commands.AuthenticateByAccessToken(
                security_data=request.headers["Authorization"]
            )
            uow = DjangoORMUnitOfWork()

            result = messagebus.handle(cm, uow)
        except InvalidSecurityData as msg:
            return Response({"message": str(msg)}, status=HTTP_401_UNAUTHORIZED)

        return Response(data=result, status=HTTP_204_NO_CONTENT)


class RequestRestorePasswordView (APIView):
    def post(self, request):
        try:
            serializer = RequestRestorePasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            cmd = commands.RequestRestorePassword(
                serializer.validated_data["email"],
                serializer.validated_data["login"]
            )
            uow = DjangoORMAndRedisClientUnitOfWork(redis_client)
            messagebus.handle(cmd, uow)
        except (RestorePasswordRequestAlreadyExists, UserNotFound) as msg:
            return Response({"message": str(msg)}, status=HTTP_400_BAD_REQUEST)

        return Response({"message": "Email sent"}, status=HTTP_200_OK)


class RestorePasswordView(APIView):
    def post(self, request):
        try:
            serializer = RestorePasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            cmd = commands.RestorePassword(
                serializer.validated_data["uuid"],
                serializer.validated_data["new_password"]
            )
            uow = DjangoORMAndRedisClientUnitOfWork(redis_client)
            messagebus.handle(cmd, uow)
        except RestorePasswordRequestNotFound as msg:
            return Response({"message": str(msg)}, status=HTTP_400_BAD_REQUEST)

        return Response({"message": "Password changed"}, status=HTTP_204_NO_CONTENT)

    def put(self, request):
        try:
            serializer = ChangePasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            uow = DjangoORMUnitOfWork()
            login = authenticate(request, uow)
            cmd = commands.ChangePassword(
                login,
                serializer.validated_data["new_password"]
            )
            messagebus.handle(cmd, uow)
        except (UserAlreadyExists, KeyError) as msg:
            return Response({"message": str(msg)}, status=HTTP_400_BAD_REQUEST)

        return Response({"message": "Password changed"}, status=HTTP_204_NO_CONTENT)


#
# @app.route("/allocate", methods=["POST"])
# def allocate_endpoint():
#     try:
#         cmd = commands.Allocate(
#             request.json["orderid"], request.json["sku"], request.json["qty"]
#         )
#         uow = SqlAlchemyUnitOfWork()
#         results = messagebus.handle(cmd, uow)
#         batchref = results.pop(0)
#     except InvalidSku as e:
#         return {"message": str(e)}, 400
#
#     return {"batchref": batchref}, 201
