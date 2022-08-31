#!/bin/bash
cd /opt/improved_intra_server/
source .venv/bin/activate
export DEBUG=False
gunicorn -w 4 --bind 127.0.0.1:8000 --access-logfile access.log --error-logfile error.log wsgi:app
