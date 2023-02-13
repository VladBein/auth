from django.db.models import Model, CharField


class User(Model):
    class Meta:
        db_table = "user"

    first_name = CharField(max_length=255)
    last_name = CharField(max_length=255)
    patronymic = CharField(max_length=255)
    email = CharField(max_length=255, unique=True)
    login = CharField(max_length=255, unique=True)
    password = CharField(max_length=128)
