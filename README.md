# Example Django application with the functionalities:
- ### user registration
- ### user authorization
- ### user authentication
- ### changing the user password
- ### user password restore

# Authentication is done using JSON Web Tokens (JWT):
- ### access
- ### refresh

# The application architecture was designed based on DDD (domain-driven design) and Event-Driven. Were used following patterns: repository, service-layer, UoW ...

***

## Building the containers
```sh
docker compose build
docker compose up -d app
# test
docker compose run --rm app sh -c "python manage.py test"
```

## Creating a local virtualenv (optional)
```sh
python3.10 -m venv .venv && source .venv/bin/activate # or however you like to create virtualenvs
pip install -e src/
# python src/project/manage.py ...
```
