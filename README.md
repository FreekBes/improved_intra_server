# Back-end for Improved Intra
This repository contains the back-end for use with the [Improved Intra](https://github.com/FreekBes/improved_intra) browser extension.

Improved Intra **4.0.0 and newer** are supported. Support for 3.x was dropped:
the endpoints it used (`connect.php`, `options.php`, `update.php`,
`testkey.php`, `delete.php` and `settings/<login>.json`) are gone, and those
paths now return 404. Releases up to 4.4.x still request `outstandings.php`
and `imagery.php`, which redirect to `/v2/outstandings/<login>` and
`/v2/banners`.


## Deploy with Docker

This repository ships a Dockerfile and `docker-compose.yml` to run the Improved Intra back-end. Docker is the only supported way to run it, in development as well as in production: there is no bare-metal setup.

Supported on Linux (Debian/Ubuntu tested). You need Docker with the Compose v2 plugin: every command below uses `docker compose`, which the older `docker-compose` package does not provide.

### Quick start

1. Install Docker & docker-compose (example for Debian/Ubuntu):

```sh
sudo apt update
sudo apt install -y docker.io docker-compose-v2
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

The application and the database container read the same `POSTGRES_*` names out of `.private.env`, so changing the credentials there is enough; nothing has to be kept in step by hand.

4. Create the data directory before the first start. Docker would otherwise create it as root, and you would need sudo to read or delete anything in it:

```sh
mkdir -p data/logs data/banners data/pgdata
```

5. Start the stack:

```sh
docker compose up -d --build
```

The compose stack contains two services:
- `iintra_server` (this application, served with Gunicorn)
- `iintra_database` (Postgres 16)

The application serves its own static files, so no reverse proxy is needed to run or develop against it. It is published on port 8000; open <http://127.0.0.1:8000> and you have the whole thing.

The application container runs as an unprivileged user (uid 1000) and runs two processes, started by `app/entrypoint.sh`: the scheduled runners and the Gunicorn workers. Keeping the scheduler out of the workers means the jobs fire exactly once regardless of how many workers there are, so `GUNICORN_WORKERS` (default 2) and `GUNICORN_THREADS` (default 4) can be raised freely.

All persistent state is bind-mounted from `./data`, which is gitignored: `data/pgdata` (the database), `data/banners` (user-uploaded banners) and `data/logs` (log files). Back up that one directory and you have everything.

6. Check logs and health:

```sh
docker compose logs -f
# or follow a single service
docker compose logs -f iintra_server
```

7. Stop and remove the containers:

```sh
docker compose down
```

Nothing under `./data` is touched by this, so the database, banners and logs all survive a `down`, a rebuild or an image change. Delete that directory by hand to start from scratch.

### Putting a reverse proxy in front (production)

The stack deliberately contains no web server of its own. In production, terminate TLS on whatever reverse proxy you already run and point it at port 8000; the application serves the static files itself, so the proxy needs no access to this repository.

Example nginx configurations are in `deploy/nginx/`: `iintra.example.conf` for plain HTTP and `iintra.example.ssl.conf` for TLS with an HTTP redirect.

Port 8000 is published on all interfaces. If the proxy runs on the same host, restrict it by changing the mapping in `docker-compose.yml` to `127.0.0.1:8000:8000`; otherwise make sure the port is firewalled.

### Updating the server (Docker)

To update after pulling new changes:

```sh
git pull
diff .private.env.example .private.env   # check whether new variables appeared
docker compose up -d --build
```

Do not copy `.private.env.example` over `.private.env`: that replaces your
secrets with the placeholders. Compare the two and add anything missing by hand.

If you need to rebuild everything and refresh images:

```sh
docker compose up -d --build
```

## Database migrations

The application creates its tables with SQLAlchemy's `create_all()`, which only
ever adds things. Anything that has to be dropped or altered goes in a numbered
SQL file under `app/migrations/`.

`app/init_db.py` runs them at startup, before the workers and the scheduler
start: each file is applied once, in filename order, in its own transaction,
and recorded in a `schema_migrations` table. Re-running is a no-op, and a fresh
install applies them all against an empty database, which is why they have to
be written so that doing nothing is valid (`DROP TABLE IF EXISTS`, and so on).

To add one, drop a `NNN_description.sql` file in that directory. There is no
down-migration: restore from `./data/pgdata` if one goes wrong.

## Logs

Everything is logged twice: to the container's stdout/stderr, and to files in `./data/logs`.

```sh
docker compose logs -f                  # all services
docker compose logs -f iintra_server    # just the application
```

Docker keeps at most 5 × 10 MB of stdout per container. The files are rotated by a scheduled job just after midnight and kept for 30 days; set `LOG_RETENTION_DAYS` to change that. The files are:

- `logs/access.log` — access requests
- `logs/error.log` — Gunicorn and application errors
- `logs/server.log` — application logging from the web workers
- `logs/scheduler.log` — the scheduled runners

They are readable straight from the host:

```sh
tail -n 200 ./data/logs/error.log
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

The extension requests `https://iintra.freekb.es`, but the stack only listens
on port 8000 over plain HTTP, so pointing the hosts file at it is not enough on
its own: you also need something terminating TLS on port 443 and proxying to
8000. The configurations in `deploy/nginx/` do that, and a self-signed
certificate is fine, which is what the next section is about. Browsing to
<http://127.0.0.1:8000> directly needs none of this.

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
