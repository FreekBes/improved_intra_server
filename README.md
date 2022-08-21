# Back-end for Improved Intra
This repository contains the back-end for use with the [Improved Intra](https://github.com/FreekBes/improved_intra) browser extension.


## Requirements

### Install PostgreSQL
```sh
sudo apt install -y wget
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update && sudo apt install -y postgresql
```

### Install python3 and dependencies
```sh
sudo apt install -y python3 python3-pip libpq-dev
pip install virtualenv
```

### Create PostgreSQL database (optional)
```sh
sudo -u postgres psql postgres
```
```postgresql
CREATE DATABASE "iintra" WITH OWNER "postgres" ENCODING 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';
```


## Setup

Initialize the virtual environment:
```sh
# After 15.1.0
virtualenv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Before 15.1.0
virtualenv --no-site-packages --distribute .venv && source .venv/bin/activate && pip install -r requirements.txt
```

Or, if already initialized, start the virtual environment:
```sh
source .venv/bin/activate
```
