import pyzipper
from backupxLib.initialize_loggers import setup_loggers

error_logger, _ = setup_loggers()

def list_zip_contents(archive_path: str, password: str | None) -> list[str]:
    """
    Returns a list of the contents of a ZIP (AES-encrypted or not) archive.

    :param archive_path: Path to the .zip archive
    :param password: Password if the archive is encrypted (optional)
    :return: List of file and directory names inside the archive
    """
    try:
        with pyzipper.AESZipFile(archive_path, 'r') as archive:
            if password:
                archive.setpassword(password.encode())

            return archive.namelist()

    except Exception as error:
        error_logger.error(f"Error listing contents of '{archive_path}': {str(error)}", exc_info=True)
        return []
