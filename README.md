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
