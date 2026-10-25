# Back-end for Improved Intra
This repository contains the back-end for use with the [Improved Intra](https://github.com/FreekBes/improved_intra) browser extension.


## Deploy with Docker

This repository ships a Dockerfile and `docker-compose.yml` to run the Improved Intra back-end. Docker is the only supported way to run it, in development as well as in production: there is no bare-metal setup.

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
git clone https://github.com/FreekBes/improved_intra_server.git
cd improved_intra_server
```

3. Create the secret environment file used by the application. The app loads `.private.env` at runtime; an example is provided in the repository.

```sh
cp .private.env.example .private.env
# Edit .private.env and fill in the values (SESSION_KEY, INTRA credentials, etc.)
```

Note: non-secret defaults live in `.public.env`, which is committed and baked into the image, so you only need to fill in `.private.env`. Anything set in `.private.env` (or in the environment) overrides `.public.env`.

If you change `PSQL_USER`, `PSQL_PASS` or `PSQL_DB`, start the stack with `docker compose --env-file .private.env up -d` so the database container is created with the same credentials the app uses. With the defaults, plain `docker compose up -d` is fine.

4. Start the stack:

```sh
docker compose up -d --build
```

The compose stack contains two services:
- `iintra_server` (this application, served with Gunicorn)
- `db` (Postgres 16)

The application serves its own static files, so no reverse proxy is needed to run or develop against it. It is published on `127.0.0.1:8000`; open <http://127.0.0.1:8000> and you have the whole thing.

Three named volumes hold the state that must outlive the containers: `pgdata` (the database), `banners` (user-uploaded banners) and `app_logs` (log files).

5. Check logs and health:

```sh
docker compose logs -f
# or follow a single service
docker compose logs -f iintra_server
```

6. Stop and remove containers (keep data):

```sh
docker compose down
```

Remove containers and volumes (this deletes the database, the uploaded banners and the logs):

```sh
docker compose down -v
```

### Putting a reverse proxy in front (production)

The stack deliberately contains no web server of its own. In production, terminate TLS on whatever reverse proxy you already run and point it at `127.0.0.1:8000`; the application serves the static files itself, so the proxy needs no access to this repository.

Example nginx configurations are in `deploy/nginx/`: `iintra.example.conf` for plain HTTP and `iintra.example.ssl.conf` for TLS with an HTTP redirect.

If the proxy runs on another host, change the published port in `docker-compose.yml` from `127.0.0.1:8000:8000` to `8000:8000` and firewall it appropriately.

### Updating the server (Docker)

To update after pulling new changes:

```sh
git pull
cp .private.env.example .private.env  # only if you need new variables, edit as necessary
docker compose build iintra_server
docker compose up -d
```

If you need to rebuild everything and refresh images:

```sh
docker compose up -d --build
```

## Logs

Everything is logged twice: to the container's stdout/stderr, and to files inside the `app_logs` volume.

```sh
docker compose logs -f                  # all services
docker compose logs -f iintra_server    # just the application
```

Docker keeps at most 5 × 10 MB of stdout per container. The files in the volume are rotated daily and kept for 30 days; set `LOG_RETENTION_DAYS` to change that. The files are:

- `logs/access.log` — access requests
- `logs/error.log` — Gunicorn and application errors
- `logs/server.log` — application logging (runners, API calls)

To read them inside the container, or copy them out:

```sh
docker compose exec iintra_server tail -n 200 logs/error.log
docker compose cp iintra_server:/app/logs ./logs
```

## Resetting all user/extension sessions
If you wish to reset all extension sessions, effectively logging out all extension sessions, you can do so by changing the _SESSION_KEY_ in the `.private.env` file. This will invalidate all existing Flask server sessions and force the extension to reauthenticate the user. Normally, this would happen without the user having to do anything - because of the `ext_token` or `user_token` implementation. However, if you wish to force the user to reauthenticate by logging in to the Intranet again, you also do this by deleting all `user_tokens` from the database **(use with caution)**:
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
