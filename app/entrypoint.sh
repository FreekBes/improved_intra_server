#!/usr/bin/env bash
#
# Container entrypoint: one-off database setup, then the scheduler and the web
# workers as two separate processes.
#
# This script is PID 1 (behind tini, see `init: true` in docker-compose.yml), so
# it has to forward termination signals itself and must not outlive either of
# its children: if one dies the container exits and Docker restarts the whole
# thing, rather than leaving it half working.

set -euo pipefail

cd "$(dirname "$0")"

LOG_DIR="${LOG_DIR:-logs}"
APP_USER="${APP_USER:-iintra}"

# logs/ and static/banners are bind mounts, which Docker creates owned by root.
# Take them over while still privileged, then re-exec this script unprivileged.
if [ "$(id -u)" = "0" ]; then
	chown -R "$APP_USER:$APP_USER" "$LOG_DIR" static/banners 2>/dev/null || true
	exec setpriv --reuid="$APP_USER" --regid="$APP_USER" --init-groups "$0" "$@"
fi

# Runs to completion before anything else starts, so the web workers and the
# scheduler never race each other over the schema or the default rows.
python init_db.py

scheduler_pid=""
gunicorn_pid=""

shutdown() {
	trap - TERM INT
	[ -n "$scheduler_pid" ] && kill -TERM "$scheduler_pid" 2>/dev/null || true
	[ -n "$gunicorn_pid" ] && kill -TERM "$gunicorn_pid" 2>/dev/null || true
	wait
}
trap shutdown TERM INT

# The scheduler writes to its own log file: one writer per file keeps the
# rotation in the logging configuration deterministic.
LOG_FILE_SERVER="${LOG_DIR}/scheduler.log" python scheduler.py &
scheduler_pid=$!

gunicorn wsgi:app &
gunicorn_pid=$!

# Wake up as soon as either process exits, whichever it is.
set +e
wait -n
status=$?
set -e

shutdown
exit "$status"
