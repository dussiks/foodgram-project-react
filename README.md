![foodgram workflow](https://github.com/dussiks/foodgram-project-react/actions/workflows/foodgram.yml/badge.svg)

# foodgram

Foodgram API application that allows to operating with Recipes by making http calls. App provides authorization and authentification services.


## Installation

Application consists of three Docker images:
- backend - image of application
- postgres - Postgres v.12 database image
- nginx - nginx web-server image

1. Clone the project:
 
```bash
git clone https://github.com/dussiks/foodgram-project-react
```

2. Install Docker (https://docs.docker.com/engine/install/)
3. Shift to project directory:

```bash
cd backend
```

4. Rename file dev.env to .env
5. Run docker-compose command:

```bash
docker-compose up -d
```

## Running

Need to adjust db and static and after application started

### Django settings
```bash
docker-compose exec backend python manage.py migrate --noinput
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input 
```
Application settings pointed in 'backend/foodgram/settings'


### Detailed documentation for API you could see via url: ```/api/docs/```


## Author
Ildus Islamov
