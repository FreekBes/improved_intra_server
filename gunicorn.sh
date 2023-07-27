#!/bin/bash
cd /opt/improved_intra_server/
source .venv/bin/activate
export DEBUG=False
gunicorn -w 1 --bind 127.0.0.1:8000 --access-logfile logs/access.log --error-logfile logs/error.log wsgi:app
