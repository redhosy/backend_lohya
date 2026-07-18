#!/bin/sh
set -e

echo "Waiting for database to be ready..."
while ! python -c "
import sys
try:
    from sqlalchemy import create_engine
    import os
    url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/pantau_cabai')
    engine = create_engine(url)
    conn = engine.connect()
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    echo "Database not ready, retrying in 2s..."
    sleep 2
done
echo "Database is ready!"

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
