import os
from datetime import datetime, timedelta
from backupxLib.initialize_loggers import setup_loggers

error_logger, info_logger = setup_loggers()

def delete_backups(path_dir):
    """Delete backups older than 3 months based on datetime in filename"""
    try:
        if not os.path.isdir(path_dir):
            error_logger.error(f"Directory not found: {path_dir}")
            return

        now = datetime.now()
        threshold = now - timedelta(days=90)

        for file in os.listdir(path_dir):
            file_path = os.path.join(path_dir, file)

            if os.path.isfile(file_path):
                    base = os.path.splitext(file)[0]
                    parts = base.split("_")

                    if len(parts) < 3:
                        continue

                    date_str = f"{parts[1]}_{parts[2]}"
                    file_datetime = datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")

                    if file_datetime < threshold:
                        os.remove(file_path)
                        info_logger.info(f"Deleted old backup: {file}")

    except Exception as error:
        error_logger.error(f"Error: {str(error)}", exc_info=True)
