import py7zr
import os
import sys
from backupxLib.initialize_loggers import setup_loggers

error_logger, info_logger = setup_loggers()

# Store the current working
current_directory = os.getcwd()

def create_7z(archive_name: str, source_path: str, compression_level: int, password: str | None, encryption: bool) -> None:
    """
    Creates a .7z archive with configurable compression level.

    :param archive_name: Output .7z archive filename (including .7z extension)
    :param source_path: Path to the file or directory to compress
    :param compression_level: Compression level (0-9), where 0 = Store (fastest) and 9 = Maximum compression (slowest)
    """
    try:

        parent_dir = os.path.dirname(source_path)
        os.chdir(parent_dir)
        source_path = os.path.basename(source_path)

        with py7zr.SevenZipFile(
            archive_name,
            'w',
            filters=[{'id': py7zr.FILTER_LZMA2, 'preset': compression_level}]
        ) as archive:
            archive.writeall(source_path)
            source_path = os.path.abspath(source_path)
            os.chdir(current_directory)

        if password and encryption:
             archive_name += '.aes'

        info_logger.info(
            f"\nArchive '{archive_name}' created successfully from '{source_path}' "
            f"\nWith compression level: {str(compression_level)} "
        )

    except Exception as error:
        error_logger.error(f"Error creating 7z archive '{archive_name}': {str(error)}", exc_info=True)
        sys.exit(1)
