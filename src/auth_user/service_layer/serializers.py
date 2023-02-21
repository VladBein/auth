from rest_framework.serializers import Serializer
from rest_framework.fields import CharField, EmailField


class UserSerializer(Serializer):
    first_name = CharField(max_length=255)
    last_name = CharField(max_length=255)
    patronymic = CharField(max_length=255)
    email = EmailField(max_length=255)
    login = CharField(max_length=255)


class UserWithPasswordSerializer(UserSerializer):
    password = CharField(max_length=128)


class EmailAndLoginSerializer(Serializer):
    email = CharField(max_length=128)
    login = CharField(max_length=128)


class UUIDSerializer(Serializer):
    uuid = CharField(max_length=128)


class NewPasswordSerializer(Serializer):
    new_password = CharField(max_length=128)


class UUIDAndNewPasswordSerializer(UUIDSerializer, NewPasswordSerializer):
    ...
