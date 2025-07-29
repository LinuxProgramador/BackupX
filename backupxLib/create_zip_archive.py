import pyzipper
import os
import sys
from backupxLib.initialize_loggers import setup_loggers

error_logger, info_logger = setup_loggers()

# Store the current working
current_directory = os.getcwd()

def create_zip_aes(archive_name: str, source_path: str, password: str | None, compression_level: int) -> None:
    """
    Creates a ZIP archive with optional AES-256 encryption and configurable compression level using pyzipper.

    :param archive_name: Output .zip archive name
    :param source_path: Path to file or folder to compress
    :param password: Optional password for AES-256 encryption
    :param compression_level: Compression level (0-9), 0 = Store (no compression), 9 = Maximum compression
    """
    try:

        parent_dir = os.path.dirname(source_path)
        os.chdir(parent_dir)

        # Select ZIP class depending on whether a password is provided
        if password:
            archive = pyzipper.AESZipFile(
                archive_name,
                'w',
                compression=pyzipper.ZIP_DEFLATED,
                encryption=pyzipper.WZ_AES,
                compresslevel=compression_level
            )
            archive.setpassword(password.encode())
            archive.setencryption(pyzipper.WZ_AES)
        else:
            archive = pyzipper.ZipFile(
                archive_name,
                'w',
                compression=pyzipper.ZIP_DEFLATED,
                compresslevel=compression_level
            )

        with archive:

            if os.path.isdir(source_path):
                for root, _, files in os.walk(source_path):
                    for file in files:
                        filepath = os.path.join(root, file)
                        arcname = os.path.relpath(filepath, start=parent_dir)
                        archive.write(filepath, arcname)
            else:
                arcname = os.path.relpath(source_path, start=parent_dir)
                archive.write(source_path, arcname)


        os.chdir(current_directory)

        info_logger.info(
            f"\nArchive '{archive_name}' created successfully from '{source_path}' "
            f"\nWith compression level: {str(compression_level)} "
        )

    except Exception as error:
        error_logger.error(f"Error creating ZIP archive '{archive_name}': {str(error)}", exc_info=True)
        sys.exit(1)


