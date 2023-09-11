# Planetarium API

This is Planetarium APi Service writen using Django Rest Framework. It is created for managing astronomy shows, reservations tickets and other.

## Features
* CRUD operations for show themes, planetarium dome, astronomy show, show session
* Add images fo astronomy shows
* Filtering show session by date, astronomy show and planetarium dome

## Installation
To set up and run this project follow next steps.

Python must be installed

### Clone the repository
```python
https://github.com/kovaliskoveronika/planetarium-api.git
```

### Create .env file and define variables following .env.sample

### Built Docker container
```python
docker-compose build
```

### Access list of containers
```python
docker ps -a
```

### Create a superuser
```python
docker exec -it <container_id here> python manage.py createsuperuser
```

### Start the Docker container
```python
docker-compose up
```

### To stop the container
```python
docker-compose down
```

## Endpoints
```python
          "show_themes": "http://localhost:8000/planetarium/show_themes/",
          "planetarium_domes": "http://localhost:8000/planetarium/planetarium_domes/",
          "astronomy_show": "http://localhost:8000/planetarium/astronomy_show/",
          "show_sessions": "http://localhost:8000/planetarium/show_sessions/",
          "reservations": "http://localhost:8000/planetarium/reservations/"
          "register": "http://localhost:8000/user/register",
          "me": "http://localhost:8000/user/me",
          "token": "http://localhost:8000/user/token",
          "refresh": "http://localhost:8000/user/token/refresh/",
          "verify": "http://localhost:8000/user/token/verify/",
```
