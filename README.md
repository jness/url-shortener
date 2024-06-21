# URL Shortener 

`This is a demo and proof of concept, it should not be leveraged for any meaningful work`

This is a simple Flask application for shortening full urls to random strings,
and then looking them up by that short string.

The front-end consits of `Gunicorn` WSGI server passing to a `Flask` python application.

The back-end consists of a `Redis` cache for quick lookup, and `MongoDB` for long
term storage.

With this setup we can easily add more front-end servers, we could also easily
loadbalance those services with something like `haproxy` or reverse `nginx`.

## Requirements

  * Docker
  * docker-compose

## Startup

Using `docker-compose` start up the 3 node stack (Gunicorn, Redis, Mongo)

```
$ docker-compose up
```

## Usage

In order to get a short string for a full url in the application you need to `POST` to our endpoint:

```
$ curl -X POST -H "Content-Type: application/json" -d '{"full_url": "http://nessy.info"}' http://localhost:8000/url/shorten
mtbl1j
```

Once the string is known we can go in reverse with a simple `GET`

```
$ curl http://localhost:8000/r/mtbl1j
http://nessy.info
```

If a short string is not stored a `HTTP 404` will be returned:

```
$ curl -i http://localhost:8000/r/mtbl1
HTTP/1.1 404 NOT FOUND
Server: gunicorn
Date: Fri, 21 Jun 2024 21:06:48 GMT
Connection: close
Content-Type: text/html; charset=utf-8
Content-Length: 20
```

## Improvement

Below I will list some improvements and things to keep in mind

* In a production environment we would setup both Redis and MongoDB in HA
* We would take backups of the MongoDB persitent database
* Redis should be fully a cache in this setup, lookups that don't hit cache and that are in MongoDB will be cached.
* I would decorate our POST functions to check for some form of authentication/authorization (tokens)
* Write unit test for each of the low level functions (this would be fairly easy as the logic isn't too complex)
