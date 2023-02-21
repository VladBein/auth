FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /src/project

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY tests/ /tests/

COPY src/ /src/
RUN pip install -e /src

CMD python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000
