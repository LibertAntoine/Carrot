#!/bin/bash
cd src
if [ -z "${JUMPER_PORT}" ]; then
    export JUMPER_PORT=9890
fi
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python -m gunicorn jumper.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$JUMPER_PORT
```