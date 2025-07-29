import pyzipper
import os
import sys
from backupxLib.initialize_loggers import setup_loggers

error_logger, info_logger = setup_loggers()

def is_within_directory(base_dir: str, target_path: str) -> bool:
    """
    Checks if the target path is safely within the base directory (prevents Zip-Slip).
    """
    base_dir = os.path.abspath(base_dir)
    target_path = os.path.abspath(target_path)
    return os.path.commonpath([base_dir]) == os.path.commonpath([base_dir, target_path])

def extract_zip_aes(archive_name: str, destination: str, password: str | None) -> None:
    """
    Securely extracts a ZIP archive with optional AES-256 decryption using pyzipper.
    Validates internal paths to prevent Zip-Slip attacks.

    :param archive_name: Path to the .zip archive
    :param destination: Extraction destination folder
    :param password: Optional password for decryption
    """
    try:
        with pyzipper.AESZipFile(archive_name, 'r') as archive:
            if password:
                archive.setpassword(password.encode())

            for member in archive.namelist():
                # Compute the full output path
                target_path = os.path.join(destination, member)

                # Check for Zip-Slip vulnerability
                if not is_within_directory(destination, target_path):
                    error_logger.error(f"Zip-Slip attempt detected: {member}")
                    sys.exit(1)

                # Create directory if needed before extraction
                os.makedirs(os.path.dirname(target_path), exist_ok=True)

                # Extract file
                with archive.open(member) as source_file, open(target_path, 'wb') as target_file:
                    target_file.write(source_file.read())

        info_logger.info(f"Archive '{archive_name}' extracted successfully to '{destination}'.")

    except Exception as error:
        error_logger.error(f"Error extracting archive '{archive_name}': {str(error)}", exc_info=True)
        sys.exit(1)
