FROM alpine:3.24

RUN apk add --no-cache logrotate

COPY iintra.conf /etc/logrotate.d/iintra
# logrotate ignores configuration files that are group- or world-writable
RUN chmod 644 /etc/logrotate.d/iintra

# Containers have no cron by default, so run logrotate on a plain daily loop.
CMD ["sh", "-c", "while true; do logrotate -s /var/lib/logrotate.status /etc/logrotate.conf; sleep 86400; done"]
