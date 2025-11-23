#!/bin/bash
cd src
if [ -z "${CARROT_PORT}" ]; then
    export CARROT_PORT=9890
fi
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python -m gunicorn _config.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$CARROT_PORT
```