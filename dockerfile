FROM python:3.9.17-bullseye AS build

WORKDIR /opt/improved_intra_server

COPY . /opt/improved_intra_server

RUN pip install -r requirements.txt

CMD ./gunicorn.sh
