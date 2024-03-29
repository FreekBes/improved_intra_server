# Back-end for Improved Intra
This repository contains the back-end for use with the [Improved Intra](https://github.com/FreekBes/improved_intra) browser extension.


## Install
This guide is written with Debian 11 ("Bullseye") in mind. It should also work on Windows Subsystem for Linux.

### Update & install system dependencies
```sh
sudo apt update && sudo apt upgrade
sudo apt install git nginx openssl
```

### Clone the repository
```sh
git clone https://github.com/FreekBes/improved_intra_server.git /opt/improved_intra_server
sudo chown -R www-data:www-data /opt/improved_intra_server
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
sudo chown -R www-data:www-data /opt/improved_intra_server

# Activate the virtual environment
. .venv/bin/activate

# Install packages
sudo .venv/bin/pip install -r requirements.txt
```

### Set up secrets
Copy the `.secret.env.example` file, rename it to `.secret.env` and fill it in.

### Configure the systemd service
```sh
cp useful/iintra-server.service /etc/systemd/system/
sudo systemctl start iintra-server.service
sudo systemctl enable iintra-server.service
```

### Set up nginx as reverse-proxy
```sh
# Copy custom nginx config snippets
cp ./useful/*.nginx.snippet.conf /etc/nginx/snippets/

# Remove default nginx server
rm -f /etc/nginx/sites-enabled/default
```

#### Use with self-signed certificate
```sh
# Create SSL certificate for HTTPS support
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -newkey rsa:2048 -x509 -days 365 -nodes \
	-keyout /etc/nginx/ssl/server.key -out /etc/nginx/ssl/server.pem \
	-subj "/C=NL/ST=North-Holland/L=Amsterdam/O=ImprovedIntra/CN=iintra.freekb.es/"

# Copy server config
cp ./useful/nginx.example.ssl.conf /etc/nginx/sites-available/iintra.freekb.es.conf
ln -s /etc/nginx/sites-available/iintra.freekb.es.conf /etc/nginx/sites-enabled/

# Restart nginx
sudo systemctl restart nginx
```

#### Use without SSL support
Useful if you want to add a certificate yourself, for example using `certbot`.
```sh
# Copy server config
cp ./useful/nginx.example.conf /etc/nginx/sites-available/iintra.freekb.es.conf
ln -s /etc/nginx/sites-available/iintra.freekb.es.conf /etc/nginx/sites-enabled/

# Restart nginx
sudo systemctl restart nginx
```


## Updating the server
```sh
# Pull latest updates
cd /opt/improved_intra_server
git pull

# Activate the virtual environment
. .venv/bin/activate

# Install and update dependencies
sudo .venv/bin/pip install -r requirements.txt

# Fix permissions
sudo chown -R www-data:www-data /opt/improved_intra_server

# Restart the wsgi server
cp useful/iintra-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart iintra-server.service

# Update nginx snippets
cp ./useful/*.nginx.snippet.conf /etc/nginx/snippets/

# Do not run this step if you do not use a self-signed certificate but do use SSL/HTTPS
cp ./useful/nginx.example.conf /etc/nginx/sites-available/iintra.freekb.es.conf

# Restart nginx
sudo systemctl restart nginx
```


## Logs
There are several log files used by the Improved Intra server:
- *logs/access.log*: contains all requests made to the server
- *logs/error.log*: contains all errors encountered by the server
- *logs/server.log*: contains specific logging done by the server, such as requests made to the Intra API and logging for runners
- *wsgi.log*: contains all logging done in development mode

Additionally, there is another log maintained by the systemd service. This log contains errors encountered by the systemd service itself, such as errors encountered when starting the server. But also, very importantly: errors encountered by the server itself are logged here as well (any `print` statement). This is probably the most important log file to look at when something goes wrong.
```sh
# To view the log
sudo journalctl -u iintra-server.service

# To view the last 100 lines of the log
sudo journalctl -u iintra-server.service -n 100 --no-pager

# Or, to follow the log (like with tail -f)
sudo journalctl -u iintra-server.service -f
```


## Resetting all user/extension sessions
If you wish to reset all extension sessions, effectively logging out all extension sessions, you can do so by changing the _SESSION_KEY_ in the `.secret.env` file. This will invalidate all existing Flask server sessions and force the extension to reauthenticate the user. Normally, this would happen without the user having to do anything - because of the `ext_token` or `user_token` implementation. However, if you wish to force the user to reauthenticate by logging in to the Intranet again, you also do this by deleting all `user_tokens` from the database **(use with caution)**:
```postgresql
START TRANSACTION;
DELETE FROM user_tokens;
COMMIT;
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

## Ignoring the unsafe certificate error in Chromium-based browsers
1. Visit [iintra.freekb.es](https://iintra.freekb.es/) in your Chromium-based browser (after running above steps for your OS)
2. Select any spot in the "Your connection is not secure" page
3. Type `thisisunsafe` on your keyboard
4. Profit

This method will also work for any XMLHttpRequests sent by code! Isn't it great?
