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


class RequestRegistrationSerializer(BaseUserSerializer):
    password = CharField(max_length=128, allow_blank=False)


class ConfirmRegistrationSerializer(Serializer):
    uuid = CharField(max_length=128, allow_blank=False)


class ChangePasswordSerializer(Serializer):
    new_password = CharField(max_length=128, allow_blank=False)


class RestorePasswordSerializer(ConfirmRegistrationSerializer, ChangePasswordSerializer):
    ...


class RequestRestorePasswordSerializer(Serializer):
    email = CharField(max_length=128, allow_blank=False)
    login = CharField(max_length=128, allow_blank=False)


