#!/bin/bash
# A script to perform incremental backups using rsync
# source: https://linuxconfig.org/how-to-create-incremental-backups-using-rsync-on-linux
set -ueo pipefail
cd $(dirname $0)/..

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
cutoff_epoch=$(date -d "-30 days" +%s)
for bak_path in $(find "$BACKUP_DIR" -maxdepth 1 -mindepth 1 -type d) ; do
    bak_name=$(basename $bak_path)
    if ( echo $bak_name | grep -qP '^\d{8}_\d{6}$' ) ; then
        bak_dt=$(echo $bak_name | sed -r 's/(....)(..)(..)_(..)(..)(..)/\1-\2-\3 \4:\5:\6/')
        bak_epoch=$(date -d "$bak_dt" +%s)
        if [ $bak_epoch -lt $cutoff_epoch ]; then
            rm -rf "$bak_path"
        fi
    fi
done
