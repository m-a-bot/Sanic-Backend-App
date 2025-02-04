# Sanic-Backend-App

# installation

### with docker
```docker compose -f docker-compose.yml up -d --build```

### without docker
```poetry run sanic app.main:app --host=0.0.0.0```

# migrations

### with docker
```docker compose exec sanic_service alembic upgrade head```

### without docker
```poetry run alembic upgrade head```

# test data

```
{
    "fullname": "testadmin",
    "email": "admin@email.com",
    "password": "admin12345"
}
```

```
{
    "fullname": "testuser",
    "email": "some@email.com",
    "password": "user12345"
}
```