#!/bin/bash

# === Configuration ===
PYTHON_BIN="/usr/bin/python3"
CHANGE_PATH="cd /absolute/path/to/BackupX &&"
BACKUP_SCRIPT="backupx.py"

# NOTE: Cron logs cannot be redirected to the logs directory
LOG_FILE="/absolute/path/to/BackupX/backup.log"
CRON_SCHEDULE="0 3 * * *"

# === Basic validation ===
if [ ! -x "$PYTHON_BIN" ]; then
  echo "[ERROR] Python not found at: $PYTHON_BIN"
  exit 1
fi

if [ ! -f "$BACKUP_SCRIPT" ]; then
  echo "[ERROR] Backup script not found at: $BACKUP_SCRIPT"
  exit 1
fi

# === Cron job line ===
CRON_COMMAND="$CRON_SCHEDULE $CHANGE_PATH $PYTHON_BIN $BACKUP_SCRIPT >> $LOG_FILE 2>&1"

# === Check if the cron job already exists ===
(crontab -l 2>/dev/null | grep -F "$BACKUP_SCRIPT") >/dev/null
if [ $? -eq 0 ]; then
  echo "[INFO] Cron job is already registered. No changes made."
else
  # Add the new cron job to the current user's crontab
  (crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -
  echo "[OK] Cron job added:"
  echo "$CRON_COMMAND"
fi
