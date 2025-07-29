import os
import py7zr
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

def extract_7z(source_file: str, destination_dir: str) -> None:
    """
    Securely extracts a .7z archive to the specified destination folder with validation
    to prevent Zip-Slip attacks.

    :param source_file: Full path to the .7z archive file.
    :param destination_dir: Directory where the archive contents will be extracted.
    """
    try:
        with py7zr.SevenZipFile(source_file, mode='r') as archive:
            file_list = archive.getnames()

            for member in file_list:
                target_path = os.path.join(destination_dir, member)

                if not is_within_directory(destination_dir, target_path):
                    error_logger.error(f"Zip-Slip attempt detected in: {member}")
                    sys.exit(1)

            archive.extractall(path=destination_dir)

        info_logger.info(f"Archive '{source_file}' extracted successfully to '{destination_dir}'.")

    except Exception as error:
        error_logger.error(f"Error extracting archive '{source_file}': {str(error)}", exc_info=True)
        sys.exit(1)
