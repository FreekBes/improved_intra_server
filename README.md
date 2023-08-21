# Back-end for Improved Intra
This repository contains the back-end for use with the [Improved Intra](https://github.com/FreekBes/improved_intra) browser extension.


## First-time setup
1. Install the required software: Docker
2. Clone this repository to your server (recommended directory: `/opt/improved_intra_server`)
3. Create SSL certificate for HTTPS support:
```sh
cd /opt/improved_intra_server
sudo openssl req -newkey rsa:2048 -x509 -days 365 -nodes \
	-keyout ./useful/ssl/server.key -out ./useful/ssl/server.pem \
	-subj "/C=NL/ST=North-Holland/L=Amsterdam/O=ImprovedIntra/CN=iintra.freekb.es/"
```
4. Set up the *.secret.env* file and fill it in. See the *.secret.env.example* file for an example.
5. Modify *.public.env* if required.


## Starting the server
Simply start the Docker container:
```sh
cd /opt/improved_intra_server
docker-compose up -d
```

### Starting without Docker (not recommended)
1. Install the required software: Python 3.9+, PostgreSQL 9+
2. Create a virtual environment and install the required Python packages:
```sh
cd /opt/improved_intra_server
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Start the server:
```sh
./gunicorn.sh    # production
python3 wsgi.py  # development
```
4. It is recommended to set up a proxy nginx server in front of the Flask server, especially in production. See the *useful/iintra.freekb.es.conf* file for an example nginx configuration.


## Updating the server
Before you pull any updates and restart the server, make sure to check the changelogs for any database migrations that might be required.
If there are any, you will need to run them manually before restarting the server.


## Logs
There are several log files used by the Improved Intra server:
- *logs/access.log*: contains all requests made to the server
- *logs/error.log*: contains all errors encountered by the server
- *logs/server.log*: contains specific logging done by the server, such as requests made to the Intra API and logging for runners
- *wsgi.log*: contains all logging done in development mode (`virtualenv -p python3 venv && source venv/bin/activate && pip install -r requirements.txt && python3 wsgi.py`)


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
