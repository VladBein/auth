from rest_framework.serializers import Serializer
from rest_framework.fields import CharField, EmailField


class BaseUserSerializer(Serializer):
    first_name = CharField(max_length=255, allow_blank=False)
    last_name = CharField(max_length=255, allow_blank=False)
    patronymic = CharField(max_length=255, allow_blank=False)
    email = EmailField(max_length=255, allow_blank=False)
    login = CharField(max_length=255, allow_blank=False)


class UserDetailSerializer(BaseUserSerializer):
    ...


class RegistrationSerializer(BaseUserSerializer):
    password = CharField(max_length=128, allow_blank=False)


class AuthorizationSerializer(Serializer):
    Authorization = CharField(allow_blank=False)
