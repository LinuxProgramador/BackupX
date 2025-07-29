import py7zr
from backupxLib.initialize_loggers import setup_loggers

error_logger, _ = setup_loggers()

def list_7z_contents(archive_path: str) -> list[str]:
    """
    Returns a list of the contents of a .7z archive.

    :param archive_path: Path to the .7z archive
    :return: List of file and directory names inside the archive
    """
    try:
        with py7zr.SevenZipFile(archive_path, mode='r') as archive:
            return archive.getnames()

    except Exception as error:
        error_logger.error(f"Error listing contents of '{archive_path}': {str(error)}", exc_info=True)
        return []
