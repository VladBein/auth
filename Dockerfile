FROM python:3.10-alpine

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /src
COPY src/ /src/
RUN pip install -e /src
COPY tests/ /tests/

WORKDIR /src/project
CMD python /project/manage.py migrate && \
    python /project/manage.py runserver 0.0.0.0:5000
