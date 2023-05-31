#!/bin/bash
# A script to perform incremental backups using rsync
# source: https://linuxconfig.org/how-to-create-incremental-backups-using-rsync-on-linux
set -xueo pipefail
cd $(dirname $0)

# Paths
readonly SOURCE_DIR="$PWD/data"
readonly BACKUP_DIR="$PWD/backups"

readonly DATETIME="$(date '+%Y%m%d_%H%M%S')"
readonly BACKUP_PATH="$BACKUP_DIR/$DATETIME"
readonly LATEST_LINK="$BACKUP_DIR/latest"

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
