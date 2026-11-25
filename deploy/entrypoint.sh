#!/bin/sh
set -eu

export PORT="${PORT:-10000}"
envsubst '${PORT}' \
    < /etc/nginx/templates/default.conf.template \
    > /etc/nginx/conf.d/default.conf

if [ "${SEED_DEMO_DATA:-false}" = "true" ]; then
    python -c 'from app.database.session import SessionLocal; from app.models import User; db = SessionLocal(); exists = db.query(User).filter(User.email == "jay.verma.s1@edu.example.com").first() is not None; db.close(); raise SystemExit(0 if exists else 1)' \
        || python scripts/seed.py
fi

exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/edutrack.conf
