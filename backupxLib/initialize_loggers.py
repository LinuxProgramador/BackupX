import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def setup_loggers() -> tuple[logging.Logger, logging.Logger]:
    """
    Sets up two loggers: one for errors and one for general information.

    - Logs are saved in the 'logs' directory.
    - Uses rotating file handlers (1MB max, 3 backups).
    - Formats messages with timestamp, level, and content.
    - error_logger logs ERROR level and above to 'errors.log'.
    - info_logger logs INFO level and above to 'info.log'.
    - Log propagation is disabled to avoid duplicate entries.

    Returns:
       Tuple of (error_logger, info_logger)
    """
    try:
      os.makedirs('logs', exist_ok=True)

    except (FileExistsError, PermissionError) as e:
      print(f"[ERROR]: {e}")
      sys.exit(1)

    logs_dir = os.path.abspath('logs')

    log_format = "[%(asctime)s] %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H-%M-%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)

    max_log_size = 1024 * 1024  # 1MB
    backup_count = 3

    # Create and configure error_logger
    error_logger = logging.getLogger("error_logger")
    error_logger.setLevel(logging.ERROR)
    error_logger.propagate = False
    error_logger.handlers.clear()  # Clear previous handlers

    error_handler = RotatingFileHandler(
        os.path.join(logs_dir, "errors.log"),
        maxBytes=max_log_size,
        backupCount=backup_count,
        encoding="utf-8"
    )
    error_handler.setFormatter(formatter)
    error_logger.addHandler(error_handler)

    # Create and configure info_logger
    info_logger = logging.getLogger("info_logger")
    info_logger.setLevel(logging.INFO)
    info_logger.propagate = False
    info_logger.handlers.clear()  # Clear previous handlers

    info_handler = RotatingFileHandler(
        os.path.join(logs_dir, "info.log"),
        maxBytes=max_log_size,
        backupCount=backup_count,
        encoding="utf-8"
    )
    info_handler.setFormatter(formatter)
    info_logger.addHandler(info_handler)

    return error_logger, info_logger
