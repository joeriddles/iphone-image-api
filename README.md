# iPhone-image-api

More info coming soon...

### Dev

Install dependencies:
```shell
$ pip install -r requirements.txt
```

To run locally, use VS Code + F5 or,
```shell
$ fastapi run dev
```

To test the Dockerfile:
```shell
$ docker build . -t image-api:latest
$ docker run -p 8000:8000 --rm image-api:latest
```
