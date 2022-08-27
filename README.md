# Back-end for Improved Intra
This repository contains the back-end for use with the [Improved Intra](https://github.com/FreekBes/improved_intra) browser extension.


## Install
This guide is written with Debian 11 ("Bullseye") in mind. It should also work on Windows Subsystem for Linux.

### Update & install system dependencies
```sh
sudo apt update && sudo apt upgrade
sudo apt install git
```

### Clone the repository
```sh
git clone https://github.com/FreekBes/improved_intra_server.git /opt/improved_intra_server
cd /opt/improved_intra_server
```

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

### Configure the systemd service
```sh
sudo systemctl start ./useful/iintra-server.service
sudo systemctl enable ./useful/iintra-server.service
```

### Install and set up nginx
```sh
sudo apt install -y nginx
cp ./useful/nginx.example.conf /etc/nginx/sites-available/iintra.freekb.es.conf
ln -s /etc/nginx/sites-available/iintra.freekb.es.conf /etc/nginx/sites-enabled/iintra.freekb.es.conf
sudo systemctl restart nginx
```

## Using a self-hosted back-end server in development
On a user machine, modify the hosts file to point to your development server. Don't forget to remove those lines after development!

### Unix
```sh
# Replace 127.0.0.1 with the IP address of your server if not on localhost
sudo echo '127.0.0.1 darkintra.freekb.es' >> /etc/hosts
sudo echo '127.0.0.1 iintra.freekb.es' >> /etc/hosts
```

### Windows
1. Run `notepad.exe` as an administrator
2. Open the file `C:\Windows\System32\drivers\etc\hosts`
3. Add the following lines at the bottom of the file (replace the `127.0.0.1` with the IP address of your server if not on localhost):
```
# Improved Intra development server
127.0.0.1 darkintra.freekb.es
127.0.0.1 iintra.freekb.es
```
