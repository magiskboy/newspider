#!/bin/sh

export PYTHONPATH=.

if [ $APP == "web" ]; then
    ./venv/bin/uvicorn asgi:app --workers $(nproc) --host "0.0.0.0" --log-level error
else
    ./venv/bin/python manager.py clone
fi
