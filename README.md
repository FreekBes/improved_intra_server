# Back-end for Improved Intra
This repository contains the back-end for use with the [Improved Intra](https://github.com/FreekBes/improved_intra) browser extension.


## Deploy with Docker (recommended)

This repository now ships a Dockerfile and `docker-compose.yml` to run the Improved Intra back-end with Docker. Using Docker simplifies deployment (no system-wide Python, virtualenvs or manual Postgres installs).

Supported on Linux (Debian/Ubuntu tested). You will need Docker and docker-compose (or the Docker Compose plugin) installed on the host.

### Quick start

1. Install Docker & docker-compose (example for Debian/Ubuntu):

```sh
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable --now docker
```

2. Clone the repository and cd into it:

```sh
git clone https://github.com/FreekBes/improved_intra_server.git /opt/improved_intra_server
cd /opt/improved_intra_server
```

3. Create the secret environment file used by the application. The app loads `.secret.env` at runtime; an example is provided in the repository.

```sh
cp .secret.env.example .secret.env
# Edit .secret.env and fill in the values (SESSION_KEY, INTRA credentials, etc.)
```

Note: `docker-compose.yml` references a `.env` file for docker-compose substitution if you want to override compose-time variables. That file is optional; the compose file includes defaults. If you need to provide host-specific variables for docker-compose, create a `.env` in the repository root.

4. Start the stack:

```sh
docker-compose up -d --build
```

The compose stack contains three services:
- `db` (Postgres 16) mapped to local `./pgdata` for persisted database files
- `nginx` (official nginx image) serving static files and acting as a reverse proxy
- `intra_server` (this application, served with Gunicorn on port 8000)

By default the app is exposed on container port 8000 (mapped to host port 8000 in the compose file). Nginx in the compose file exposes host ports 8080 (HTTP) and 4430 (HTTPS) — adjust these mappings in `docker-compose.yml` if you want standard ports (80/443).

5. Check logs and health:

```sh
docker-compose logs -f
# or follow a single service
docker-compose logs -f intra_server
```

6. Stop and remove containers (keep data):

```sh
docker-compose down
```

Remove containers and volumes (will remove the Postgres data in `./pgdata`):

```sh
docker-compose down -v
```

### SSL / nginx notes

The `nginx` service mounts `./nginx/snippets` and `./nginx/conf.d` from the repository. If you want to use custom SSL certificates, create a `./nginx/certs` directory and either uncomment the certs volume in `docker-compose.yml` or add a volume mapping, then update the nginx configs in `nginx/conf.d` accordingly.

### Updating the server (Docker)

To update after pulling new changes:

```sh
git pull
cp .secret.env.example .secret.env  # only if you need new variables, edit as necessary
docker-compose build intra_server
docker-compose up -d
```

If you need to rebuild everything and refresh images:

```sh
docker-compose up -d --build
```

### When to use the old manual instructions

The repository previously documented a manual setup (installing Python, virtualenv, PostgreSQL, systemd service and nginx on the host). If you prefer a host-native installation (for example on a production server without Docker), the older instructions are still available in earlier commits. For most use-cases Docker is recommended because it isolates dependencies and simplifies upgrades.


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
