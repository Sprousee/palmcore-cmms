#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y%m%dT%H%M%S")
FILENAME="palmcore-db-$TIMESTAMP.sql.gz"

PGPASSWORD=${PGPASSWORD:-"${POSTGRES_PASSWORD:-postgres}"}
export PGPASSWORD

PGHOST=${PGHOST:-localhost}
PGPORT=${PGPORT:-5432}
PGUSER=${PGUSER:-postgres}
PGDATABASE=${PGDATABASE:-palmcore}

pg_dump --format=custom --verbose --file=- --host="$PGHOST" --port="$PGPORT" --username="$PGUSER" "$PGDATABASE" | gzip > "$BACKUP_DIR/$FILENAME"

echo "Backup created: $BACKUP_DIR/$FILENAME"
