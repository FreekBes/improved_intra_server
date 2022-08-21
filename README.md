# Back-end for Improved Intra
This repository contains the back-end for use with the [Improved Intra](https://github.com/FreekBes/improved_intra) browser extension.


## Requirements
This guide is written with Debian 11 ("Bullseye") in mind. It should also work on Windows Subsystem for Linux.

### Install PostgreSQL
```sh
sudo apt install -y wget lsb-release gnupg2
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update && sudo apt install -y postgresql
```
More installation options available [here](https://www.postgresql.org/download/).

### Set up PostgreSQL
```sh
# Enable PostgreSQL at boot
sudo systemctl enable postgresql

# Start PostgreSQL now
sudo service postgresql start

# Launch and enter a PostgreSQL console
sudo -u postgres psql postgres
```
```postgresql
--- Set password for postgres user to 'postgres' (you can modify this)
ALTER USER postgres PASSWORD 'postgres';

--- Create database (optional, __init__.py will do this for you)
CREATE DATABASE "iintra" WITH OWNER "postgres" ENCODING 'UTF8';

--- Exit PostgreSQL console
EXIT;
```

### Install Python3
```sh
sudo apt install -y python3 python3-pip python-setuptools libpq-dev python3-virtualenv virtualenv
```

### Initialize the virtual environment
```sh
# Create a virtual environment
sudo virtualenv -p python3 .venv

# Start the virtual environment
. .venv/bin/activate

# Install packages
sudo .venv/bin/pip install -r requirements.txt
```

## Starting the server
```sh
# Start the virtual environment
. .venv/bin/activate

# And start the server
python run.py
```
