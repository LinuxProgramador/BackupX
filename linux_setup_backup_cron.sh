
#!/bin/bash

# === Configuration ===
PYTHON_BIN="/usr/bin/python3"
BACKUP_DIR="/absolute/path/to/BackupX"
BACKUP_SCRIPT="backupx.py"
BACKUP_SCRIPT_VALIDATE="$BACKUP_DIR/$BACKUP_SCRIPT"
LOG_FILE="$BACKUP_DIR/backup.log"
CRON_SCHEDULE="0 3 * * *"
CRON_COMMAND="$CRON_SCHEDULE cd $BACKUP_DIR && $PYTHON_BIN $BACKUP_SCRIPT >> $LOG_FILE 2>&1"

# === Basic validation ===
if [ ! -x "$PYTHON_BIN" ]; then
  echo "[ERROR] Python not found at: $PYTHON_BIN"
  exit 1
fi

if [ ! -f "$BACKUP_SCRIPT_VALIDATE" ]; then
  echo "[ERROR] Backup script not found at: $BACKUP_SCRIPT_VALIDATE"
  exit 1
fi

# === Check if the cron job already exists ===
if crontab -l 2>/dev/null | grep -Fxq "$CRON_COMMAND"; then
  echo "[INFO] Cron job is already registered. No changes made."
else
  # Add the new cron job to the current user's crontab
  (crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -
  echo "[OK] Cron job added:"
  echo "$CRON_COMMAND"
fi
