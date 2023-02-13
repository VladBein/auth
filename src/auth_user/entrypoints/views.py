from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK

from auth_user.domain import commands
from auth_user.domain.model.authentication import Authentication
from auth_user.domain.model.user import ModelUser
from auth_user.service_layer.handlers import make_registration_request, add_user, authorize_user, create_tokens, \
    authenticate_user, change_password
from auth_user.service_layer.serializers import RegistrationSerializer, AuthorizationSerializer, \
    ChangePasswordSerializer
from auth_user.service_layer.uow import DjangoORMAndRedisClientUnitOfWork, DjangoORMUnitOfWork, UnitOfWork


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cmd = commands.RequestRegistration(
            serializer.validated_data['first_name'],
            serializer.validated_data['last_name'],
            serializer.validated_data['patronymic'],
            serializer.validated_data['email'],
            serializer.validated_data['login'],
            serializer.validated_data['password']
        )
        model_user = ModelUser(
            first_name=cmd.first_name,
            last_name=cmd.last_name,
            patronymic=cmd.patronymic,
            email=cmd.email,
            login=cmd.login,
            password=cmd.password,
            new=True
        )
        redis_client = DjangoORMAndRedisClientUnitOfWork()
        make_registration_request(cmd, redis_client)
        uuid_user = commands.ConfirmRegistration(model_user.uuid)
        data_user = add_user(uuid_user, redis_client)
        return Response(data=data_user, status=HTTP_201_CREATED)


class SecurityTokenView(APIView):
    def get(self, request):
        serializer = AuthorizationSerializer(data=request.headers)
        serializer.is_valid(raise_exception=True)
        security_data = commands.Authorize(serializer.validated_data["Authorization"])
        django_orm_uow = DjangoORMUnitOfWork()
        authorize_user(security_data, django_orm_uow)
        sub = Authentication()
        token = commands.CreateTokens(sub=sub(str(security_data)), iat=datetime.now())
        uow = UnitOfWork()
        return Response(create_tokens(token, uow), status=HTTP_200_OK)


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uow = UnitOfWork()
        security_data = commands.AuthenticateByAccessToken(serializer.validated_data["Authorization"])
        login = authenticate_user(security_data, uow)
        django_orm_uow = DjangoORMUnitOfWork()
        new_password = commands.ChangePassword(login, serializer.validated_data["new_password"])
        change_password(new_password, django_orm_uow)
        return Response("Password changed", status=HTTP_200_OK)


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
