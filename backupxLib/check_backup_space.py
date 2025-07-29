import os
import shutil
from backupxLib.initialize_loggers import setup_loggers

error_logger, info_logger = setup_loggers()


def calculate_directory_size(path: str) -> int:
    """Calculates total size of a file or directory in bytes."""
    if os.path.isfile(path):
        return os.path.getsize(path)

    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
    return total_size


def format_size(size_bytes: int) -> tuple[float, str]:
    """Converts bytes into a human-readable format."""
    units = ["Bytes", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return round(size, 2), units[i]


def has_enough_space_for_backup(
    source_path: str,
    destination_path: str,
    compression: str,
    backup_filename: str,
    password: str | None
) -> bool:
    """
    Checks if there is enough free space in the destination path to store a backup.
    """
    try:
        # Calculate source size in bytes and MB
        total_size_bytes = calculate_directory_size(source_path)
        source_size_mb = total_size_bytes // (1024 * 1024)

        # Calculate available space in destination (in MB)
        dest_dir = os.path.dirname(destination_path)
        _, _, free = shutil.disk_usage(dest_dir)
        free_mb = free // (1024 * 1024)

        # Determine output file name
        encrypted_output_path = f"{backup_filename}.aes" if compression == "7z" and password else backup_filename

        # Format size info for logging
        size_value, size_unit = format_size(total_size_bytes)

        info_logger.info(
            f"\nUncompressed source size: {size_value} {size_unit}"
            f"\nGenerated backup file name: '{encrypted_output_path}'"
            f"\nAvailable disk space: {free_mb} MB"
        )

        if free_mb < source_size_mb:
            error_logger.error(
                f"\nNot enough space at '{dest_dir}'"
                f"\nRequired: {source_size_mb} MB"
                f"\nAvailable: {free_mb} MB"
            )
            return False

        return True

    except PermissionError:
        error_logger.error("Permission denied accessing files or directories", exc_info=True)
        return False
    except Exception as error:
        error_logger.error(f"Unexpected error while checking space: {str(error)}", exc_info=True)
        return False
