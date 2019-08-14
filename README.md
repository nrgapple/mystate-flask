mySTATE backend using flask
=====

my first attempt at developing a backend for mySTATE using flask

## Useful links

[Reference to go off of on github](https://github.com/miguelgrinberg/microblog/tree/v0.4)

[Reference tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database)

## Representing Model data as JSON objects

Users:

```json
{
    "id": 123,
    "username": "susan",
    "password": "my-password",
    "email": "susan@example.com",
    "_links": {
        "self": "/api/users/123",
    }
}
```

POIs:

```json
{
    "id": 123,
    "name": "here",
    "details": "here we are... chillin wit da boys in the paaark",
    "lat": 26.0937377,
    "lng": 67.9837266,
    "_links": {
        "self": "/api/pois/123",
    }
}
```

Collection of Users:

```json
{
    "items": [
        { ... user resource ... },
        { ... user resource ... },
        ...
    ],
    "_meta": {
        "page": 1,
        "per_page": 10,
        "total_pages": 20,
        "total_items": 195
    },
    "_links": {
        "self": "http://localhost:5000/api/users?page=1",
        "next": "http://localhost:5000/api/users?page=2",
        "prev": null
    }
}
```

error structure:
```json
{
    "error": "short error description",
    "message": "error message (optional)"
}
```

