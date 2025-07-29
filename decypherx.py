
"""
Secure Archive Extractor Tool - v1.0.0
Author: J.P Rojas

Decrypts and extracts .zip or .7z archives, including AES-encrypted files (.aes).

Supported:
- .zip (with/without AES)
- .7z and .7z.aes

Main features:
- AES decryption using a password file
- Safe extraction with conflict renaming (unless --force)
- Optional content listing (--listen)
- Input validation and logging

Usage examples:
  python extractor.py -e backup.7z.aes -d key.txt -o ./restore
  python extractor.py -e archive.zip -l
"""

import argparse
import re
import sys
import os
from backupxLib.extract_zip_archive import extract_zip_aes
from backupxLib.extract_7z_archive import extract_7z
from backupxLib.initialize_loggers import setup_loggers
from backupxLib.aes_decrypt_inplace import decrypt_file
from backupxLib.get_7z_file_list import list_7z_contents
from backupxLib.get_zip_file_list import list_zip_contents

error_logger, info_logger = setup_loggers()

# Regular expressions to detect .zip and .7z/.7z.aes file types
ZIP_PATTERN = re.compile(r"\.zip$", re.IGNORECASE)
SEVENZ_PATTERN = re.compile(r"\.7z(?:\.aes)?$", re.IGNORECASE)


def rename_conflicting_files(source: str, destination: str, password: str | None, force: bool) -> None:
    """
    Renames existing files or directories in the destination to avoid overwriting.

    - Directories are renamed like: name_old, name_old_1, etc.
    - Files like: file_old.ext, file_old_1.ext, etc.
    - Skipped entirely if --force is enabled.
    """
    if force:
        return

    # Get list of files from inside the archive
    if ZIP_PATTERN.search(source):
        archive_files = list_zip_contents(source, password)
    elif SEVENZ_PATTERN.search(source):
        archive_files = list_7z_contents(source)
    else:
        return


    # Extract top-level directories from the archive paths
    root_dirs = set(re.split(r"[\\/]", entry)[0] for entry in archive_files if "/" in entry or "\\" in entry)


    # Ensure the parent directory is correctly defined
    parent_dir = os.path.dirname(destination)

    if root_dirs:
      for root_dir in root_dirs:
        potential_conflict_path = os.path.join(destination, root_dir)

        if os.path.isdir(potential_conflict_path):
            base = root_dir
            new_name = f"{base}_old"
            new_path = os.path.join(destination, new_name)
            counter = 1

            while os.path.exists(new_path):
                new_name = f"{base}_old_{counter}"
                new_path = os.path.join(destination, new_name)
                counter += 1

            os.rename(potential_conflict_path, new_path)

    else:
      if os.path.isfile(destination):
         destination = parent_dir

      for entry in archive_files:
        clean_entry = entry.rstrip("/\\")

        if not any(separator in clean_entry for separator in ["/","\\"]):
            potential_conflict_path = os.path.join(destination, clean_entry)

            if os.path.isfile(potential_conflict_path):
                base, ext = os.path.splitext(clean_entry)
                if not ext:
                  ext = ""

                new_name = f"{base}_old{ext}"
                new_path = os.path.join(destination, new_name)
                counter = 1

                while os.path.exists(new_path):
                    new_name = f"{base}_old_{counter}{ext}"
                    new_path = os.path.join(destination, new_name)
                    counter += 1

                os.rename(potential_conflict_path, new_path)



def main(source: str, destination: str, password_path: str | None, listen: bool, force: bool) -> None:
    """
    Main extraction workflow:
    - Decrypts AES-encrypted files if needed
    - Validates archive path
    - Handles renaming or overwriting
    - Extracts or lists contents based on arguments
    """
    try:

        if password_path and os.path.isfile(password_path):
          with open(password_path, 'r', encoding='utf-8') as f:
                   password = f.read().strip()
                   if len(password) >= 255:
                      error_logger.error(f"[SECURITY] The content of '{password_path}' exceeds the safe length limit (>= 255 characters). Potential buffer overflow risk")
                      sys.exit(1)

        else:
            password = None


        if source and os.path.isfile(source[:-4]):
               source = source[:-4]

        if not source or not os.path.isfile(source):
            error_logger.error(f"Backup archive not found at: '{source}'. Please verify that the file exists and the path is correct")
            sys.exit(1)

        source = os.path.abspath(source)
        os.makedirs(destination, exist_ok=True)
        destination = os.path.abspath(destination)

        if source.endswith(".aes"):
           if password:
               decrypt_file(source, password)
               os.remove(source)
               source = source[:-4]

           else:
             error_logger.error(f"Missing or invalid password for decrypted archive: {source}")
             sys.exit(1)

        rename_conflicting_files(source, destination, password, force)

        if ZIP_PATTERN.search(source) and listen:
              files = list_zip_contents(source, password)
              for file in files:
                 print(file)

        elif SEVENZ_PATTERN.search(source) and listen:
              files = list_7z_contents(source)
              for file in files:
                 print(file)

        elif ZIP_PATTERN.search(source):
            extract_zip_aes(source, destination, password)

        elif SEVENZ_PATTERN.search(source):
            extract_7z(source, destination)

        else:
            error_logger.error("Unsupported file format. Only .zip and .7z are allowed")

    except KeyboardInterrupt:
        error_logger.error("Execution interrupted by user (Ctrl+C)", exc_info=True)
        sys.exit(1)

    except Exception as error:
        error_logger.error(f"Error: {str(error)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":

    # Argument definitions:
    # -e / --extract: Required path to archive file (.zip, .7z, or .7z.aes)
    # -d / --decipher: Optional path to text file containing decryption key
    # -o / --destination: Folder to extract contents to (default: ./backups)
    # -l / --listen: Only list archive contents (no extraction)
    # -f / --force: Overwrite existing files/folders instead of renaming

    # Ensure 'backups' directory exists; create it if it doesn't
    try:
      os.makedirs('backups', exist_ok=True)

    except (FileExistsError, PermissionError):
      error_logger.error("[ERROR]: ", exc_info=True)
      sys.exit(1)

    # Argument parser setup
    parser = argparse.ArgumentParser(
        description="Decrypt and extract compressed archives (.zip, .7z)"
    )
    parser.add_argument(
        "-d", "--decipher",
        dest="decipher",
        required=False,
        type=str,
        default=None,
        metavar="KEY PATH",
        help="Path to the plain text file where the decryption key is stored"
    )
    parser.add_argument(
        "-e", "--extract",
        dest="extract",
        required=True,
        type=str,
        metavar="ARCHIVE",
        help="Path to the compressed and encrypted file (.zip or .7z)"
    )
    parser.add_argument(
        "-o", "--destination",
        dest="destination",
        required=False,
        type=str,
        default=os.path.abspath('backups'),
        metavar="FOLDER",
        help="Destination folder to extract contents to"
    )
    parser.add_argument(
        "-l", "--listen",
        dest="listen",
        action="store_true",
        help="If set, the script will list the contents inside a compressed and encrypted file (.zip or .7z)"
    )
    parser.add_argument(
        "-f", "--force",
        dest="force",
        action="store_true",
        help="Overwrite existing files or directories when extracting the archive. If not enabled, existing files will be preserved"
    )

    args = parser.parse_args()

    field_limits = {
     "extract": 1024,
     "destination": 1024,
     "decipher": 1024
    }


    backup_config = [
     args.extract,
     args.destination,
     args.decipher
    ]


    for field_name, value in zip(field_limits.keys(), backup_config):
      max_length = field_limits[field_name]
      value = '' if not value else value

      if len(value) >= max_length:
        error_logger.error(
            f"[SECURITY] Field '{field_name}' exceeds safe length: {len(value)} >= {max_length}\nPossible overflow or malformed input"
        )
        sys.exit(1)


    main(args.extract, args.destination, args.decipher, args.listen, args.force)
