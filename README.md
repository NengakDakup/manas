# project-web-app
A Django App for Flood Monitoring and Analytics


## Requirements
- Linux OS
- django
- Celery
- Redis

## Getting Started
- Create  a virtualenv
- Install requirements in virtualenv
```bash
$ pip install -r requirements.txt
```
- Setup Redis server
```
# Using Docker
$ docker run -d -p 6379:6379 redis:alpine

# Using redis
$ sudo apt install redis
$ redis-server
```

- Start Celery Server
```
$ celery -A predict worker -l info --detach
```

- Start Django Server
```
$ python manage.py runserver
```
