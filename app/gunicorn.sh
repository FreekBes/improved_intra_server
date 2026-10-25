#!/bin/bash
cd ./app
source ./venv/bin/activate
export DEBUG=False
gunicorn --bind 127.0.0.1:8000 wsgi:app
