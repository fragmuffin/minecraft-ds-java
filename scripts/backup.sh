#!/bin/bash
# A script to perform incremental backups using rsync
# source: https://linuxconfig.org/how-to-create-incremental-backups-using-rsync-on-linux
set -ueo pipefail
cd $(dirname $0)

# Paths
readonly SOURCE_DIR="$PWD/data"
readonly BACKUP_DIR="$PWD/backups"

readonly DATETIME="$(date '+%Y%m%d_%H%M%S')"
readonly BACKUP_PATH="$BACKUP_DIR/$DATETIME"
readonly LATEST_LINK="$BACKUP_DIR/latest"

# ----- Create Backup
mkdir -p "${BACKUP_DIR}"

# Perform Sync
rsync -av --delete \
  "$SOURCE_DIR/" \
  --link-dest "$LATEST_LINK" \
  --exclude=".cache" \
  "$BACKUP_PATH/"

# Cleanup
rm -rf "$LATEST_LINK"
ln -s "$BACKUP_PATH" "$LATEST_LINK"

# ----- Clean Old Backups
# Remove backups older than 30 days
find "$BACKUP_DIR" \
    -mindepth 1 \
    -maxdepth 1 \
    -type d \
    -mtime +30 \
    -exec rm -rf {} \;
