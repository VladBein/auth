from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK

# from ..adapters.repository import DjangoORMRepository
# from ..service_layer.serializers import RegistrationSerializer, AuthorizationSerializer


class UserView(APIView):
    def post(self, request):
        # serializer = RegistrationSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # response_data = registration(
        #     DjangoORMRepository(),
        #     serializer.validated_data['first_name'],
        #     serializer.validated_data['last_name'],
        #     serializer.validated_data['patronymic'],
        #     serializer.validated_data['email'],
        #     serializer.validated_data['login'],
        #     serializer.validated_data['password']
        # )
        return Response('hello1', status=HTTP_201_CREATED)


class SecurityToken(APIView):
    def get(self, request):
        # serializer = AuthorizationSerializer(data=request.headers)
        # serializer.is_valid(raise_exception=True)
        # token = authorization(DjangoORMRepository(), serializer.validated_data["Authorization"])
        # response = Response()
        # response.set_cookie(key="refresh_token", value=token.pop("refresh_token"), httponly=True)
        return Response(data="hello", status=HTTP_200_OK)


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
