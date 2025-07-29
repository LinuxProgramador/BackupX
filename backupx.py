
"""
Secure Automated Backup Tool (Linux & Windows)

This tool automates encrypted backups of files or directories with optional
remote transfer via SSH. Supports ZIP (AES-256) and 7Z formats with optional
post-encryption.

 - AES-256 encryption (native for ZIP, optional for 7Z)
 - SSH key-based transfer support
 - Safe path handling and symlink protection
 - Suitable for scheduled jobs (cron, Task Scheduler)

Author: J.P Rojas | License: GPLv3 | Version: 1.0.0 | Status: Stable
"""

__author__ = "J.P Rojas"
__version__ = "1.0.0"
__status__ = "Stable"
__license__ = "GPLv3"
__description__ = (
    "Automated backup tool. Allows secure, scheduled, "
    "and reliable backups of files and directories with minimal user interaction"
)

import configparser
import os
import time
import sys
import backupxLib.utils  # Module reserved for helper functions
from pathlib import Path
from datetime import datetime
from backupxLib.check_backup_space import has_enough_space_for_backup
from backupxLib.create_7z_archive import create_7z
from backupxLib.create_zip_archive import create_zip_aes
from backupxLib.SSHBackupManager import create_ssh_client, transfer_backup
from backupxLib.initialize_loggers import setup_loggers
from backupxLib.aes_encrypt_inplace import encrypt_file
from backupxLib.delete_old_backups import delete_backups


def establish_ssh_connection(ssh_host: str, ssh_port: int, ssh_user: str, ssh_key_path: str, error_logger: 'logging.Logger') -> 'paramiko.SSHClient':
    """
    Attempts to establish an SSH connection using the provided parameters
    Retries up to 3 times in case of failure before aborting the program

    Parameters:
        ssh_host (str): SSH server hostname or IP address
        ssh_port (int): SSH port
        ssh_user (str): Username for SSH authentication
        ssh_key_path (str): Path to the SSH private key file
        error_logger (logging.Logger): Logger for error messages

    Returns:
        paramiko.SSHClient: Connected SSH client object, or exits the program on failure
    """
    ssh = None

    for attempt in range(1, 4):
        try:
            ssh = create_ssh_client(
                hostname=ssh_host,
                port=ssh_port,
                username=ssh_user,
                key_file=ssh_key_path
            )
            break

        except Exception as error:
            error_logger.error(f"SSH connection attempt {str(attempt)} failed: {str(error)}", exc_info=True)

            if attempt == 3:
                error_logger.error("Max SSH connection attempts reached. Aborting")
                sys.exit(1)

            else:
                time.sleep(2)

    return ssh



def generate_backup_filename(destination: str,  date_and_time: str) -> str:
    """
    Appends a timestamp to the filename

    Args:
        destination (str): The full path of the output file (.zip or .7z)
        date_and_time (str): The timestamp to append to the filename

    Returns:
        str: A new file path with the timestamp inserted before the extension

    """
    filename = os.path.basename(destination).lower()
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{date_and_time}{ext}"
    generate_new_path = os.path.join(os.path.dirname(destination), new_filename)

    return os.path.abspath(generate_new_path)


def main(
    source: str,
    destination: str,
    compression: str,
    compression_level: int,
    encryption: bool,
    ssh_connection: bool,
    password: str,
    ssh_host: str,
    ssh_port: int,
    ssh_user: str,
    ssh_key_path: str,
    ssh_remote_path: str,
    ssh_local_path: str,
    date_and_time: str,
    error_logger: 'logging.Logger'
    ) -> None:
    """
    Main execution routine

    Handles:
    - Free space checking
    - Archive creation (ZIP/7Z)
    - Optional AES encryption
    - Optional SSH transfer with timestamp
    """
    try:

        if confirm_old_backup_deletion:
            delete_backups(os.path.abspath('backups'))

        # Generate the final backup filename based on the destination and timestamp
        backup_filename = generate_backup_filename(destination,  date_and_time)

        if not has_enough_space_for_backup(source, destination, compression, backup_filename, password):
            error_logger.error("Insufficient space. Backup canceled")
            sys.exit(1)


        if compression == "zip":
            create_zip_aes(backup_filename, source, password, compression_level)

        elif compression == "7z":
            create_7z(backup_filename, source, compression_level, password, encryption)
            if password and encryption:
                 encrypt_file(backup_filename, password)
                 os.remove(backup_filename)

        if ssh_connection:
          if ssh_key_path:
            if ssh_local_path == destination:
               ssh_local_path = backup_filename

            ssh = establish_ssh_connection(ssh_host, ssh_port, ssh_user, ssh_key_path, error_logger)

            try:
               transfer_backup(
                   ssh_client=ssh,
                   local_path=ssh_local_path,
                   remote_path=ssh_remote_path
               )

            finally:
                ssh.close()

          else:
            error_logger.error("Connection failed: Invalid private key path")
            sys.exit(1)

    except KeyboardInterrupt:
        error_logger.error("Execution interrupted by user (Ctrl+C)", exc_info=True)
        sys.exit(1)

    except Exception as error:
        error_logger.error(f"Error: {str(error)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":

   # Get error logger; ignore second return value
   error_logger, _ = setup_loggers()


   try:
     os.makedirs('backups', exist_ok=True)

   except (FileExistsError, PermissionError):
      error_logger.error("[ERROR]: ", exc_info=True)
      sys.exit(1)



   def load_password_source(source: str | None, ssh_validation: bool, error_logger: 'logging.Logger', home_dir: str) -> str | None:
     """
     Loads a password from a file path if valid.

     - Validates that the source is not a symlink or directory.
     - Ensures the path is within the allowed home_dir.
     - Reads and returns the password content from the file.
     - If ssh_validation is True, returns the path instead of the content.
     - Logs errors and exits on failure.
     """

     if not source:
        return None


     try:
        if os.path.islink(source):
           error_logger.error(f"Symlink detected: {source} Aborting")
           sys.exit(1)

     except Exception as error:
        error_logger.error(f"Failed to check if path is symlink: {source}. Error: {str(error)}", exc_info=True)
        return None


     if os.path.isdir(source):
        error_logger.error(f"Directory detected instead of file or value: {source} Aborting")
        sys.exit(1)


     try:
        real_source = Path(source).resolve()
        allowed_home = Path(home_dir).resolve()

     except Exception as error:
        error_logger.error(f"Error: {str(error)}", exc_info=True)
        sys.exit(1)



     try:
        real_source.relative_to(allowed_home)

     except ValueError:
        error_logger.error(f"Security violation: '{source}' is outside the allowed home_dir '{home_dir}'", exc_info=True)
        sys.exit(1)


     if os.path.isfile(source):
        if ssh_validation:
            return source

        try:
            with open(source, 'r', encoding='utf-8') as f:
                   password_str = f.read().strip()
                   if len(password_str) >= 255:
                      error_logger.error(f"[SECURITY] The content of '{source}' exceeds the safe length limit (>= 255 characters). Potential buffer overflow risk")
                      sys.exit(1)

                   return password_str

        except Exception as error:
                error_logger.error(f"Error: {str(error)}", exc_info=True)
                sys.exit(1)

     error_logger.error("The key must be provided as a file path. Raw key strings are not supported")
     sys.exit(1)


   # Gets the user's home directory regardless of whether the operating system is Linux or Windows 
   home_dir = Path.home()


   # Current date and time for timestamps
   date_and_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


   # Load config.ini
   config = configparser.ConfigParser()
   if not os.path.isfile('config.ini'):
     error_logger.error("config.ini not found")
     sys.exit(1)

   else:
     config.read('config.ini')



   # Ensure the configuration file was properly loaded and contains at least one section.
   # If not, log an error and terminate the program.
   if not config.sections():
     error_logger.error("Failed to load config.ini or it is empty")
     sys.exit(1)




   # Load backup settings: paths, compression, encryption, SSH, and password file.
   # Defaults: compression_level=1, encryption=False, ssh_connection=False.
   source = config.get('BACKUP', 'source')
   destination = config.get('BACKUP', 'destination')
   compression = config.get('BACKUP', 'compression')

   try:
      compression_level = config.getint('BACKUP', 'compression_level')

   except ValueError:
      compression_level = 1

   try:
     encryption = config.getboolean('BACKUP', 'encryption')

   except ValueError:
      encryption = False

   try:
      ssh_connection = config.getboolean('BACKUP', 'ssh_connection')

   except ValueError:
      ssh_connection = False

   try:
      confirm_old_backup_deletion = config.getboolean('BACKUP', 'confirm_old_backup_deletion')

   except ValueError:
      confirm_old_backup_deletion = False

   password_path = config.get('BACKUP', 'password_path') if encryption else None




   # Loads SSH configuration only when needed, improving code clarity and performance
   ssh_host = config.get('BACKUP', 'ssh_host') if ssh_connection else None

   try:
      ssh_port = config.getint('BACKUP', 'ssh_port') if ssh_connection else None

   except ValueError:
      ssh_port = 22

   ssh_user = config.get('BACKUP', 'ssh_user') if ssh_connection else None
   ssh_key_path = config.get('BACKUP', 'ssh_key_path') if ssh_connection else None
   ssh_remote_path = config.get('BACKUP', 'ssh_remote_path') if ssh_connection else None
   ssh_local_path = config.get('BACKUP', 'ssh_local_path') if ssh_connection else None




   # Initial validation and setup of backup parameters:
   # - Enforces safe length limits to prevent overflows or malformed input
   # - Applies default values when missing (compression type, destination path, level)
   # - Normalizes archive extension, ensures directory creation, and handles optional SSH paths

   try:

     field_limits = {
      "source": 1024,
      "destination": 1024,
      "compression": 20,
      "compression_level": 10,
      "password_path": 1024,
      "ssh_host": 255,
      "ssh_port": 10,
      "ssh_user": 255,
      "ssh_key_path": 1024,
      "ssh_remote_path": 1024,
      "ssh_local_path": 1024
     }


     backup_config = [
      source,
      destination,
      compression,
      compression_level,
      password_path,
      ssh_host,
      ssh_port,
      ssh_user,
      ssh_key_path,
      ssh_remote_path,
      ssh_local_path
     ]


     for field_name, value in zip(field_limits.keys(), backup_config):
       max_length = field_limits[field_name]
       value = '' if not value else value

       if len(str(value)) >= max_length:
         error_logger.error(
            f"[SECURITY] Field '{field_name}' exceeds safe length: {len(str(value))} >= {max_length}\nPossible overflow or malformed input"
         )
         sys.exit(1)


     if not os.path.exists(source):
       error_logger.error(f"Invalid path: '{source}'. The file or directory does not exist")
       sys.exit(1)


     if not compression:
       compression = "zip"


     compression = compression.lower()

     if compression not in ["zip","7z"]:
       compression = "zip"


     get_file_name_from_path = os.path.basename(destination).lower()

     if not any(get_file_name_from_path.endswith(ext) for ext in ['.zip', '.7z']) or not destination:
       if compression == "7z":
          output_archive = 'backup.7z'

       else:
          output_archive = 'backup.zip'
       destination = os.path.join('backups', output_archive)


     base_dir = os.path.dirname(destination)
     base_name, ext = os.path.splitext(os.path.basename(destination))

     if ext.lower() != f".{compression}":
       os.makedirs(base_dir, exist_ok=True)
       destination = os.path.join(base_dir, f"{base_name}.{compression}")


     os.makedirs(os.path.dirname(destination), exist_ok=True)


     if not 0 <= compression_level <= 9:
       compression_level = 1


     if not password_path:
       password = None


     vars_dict = {
      "ssh_host": ssh_host,
      "ssh_port": ssh_port,
      "ssh_user": ssh_user,
      "ssh_key_path": ssh_key_path,
      "ssh_remote_path": ssh_remote_path,
      "ssh_local_path": ssh_local_path,
     }

     for key, val in vars_dict.items():
       if not val:
         vars_dict[key] = None


     if encryption:
        password = load_password_source(password_path, False, error_logger, home_dir)


     if ssh_connection:
       ssh_key_path = load_password_source(ssh_key_path, ssh_connection, error_logger, home_dir)


     # Ensure absolute path
     destination = os.path.abspath(destination)
     source = os.path.abspath(source)
     ssh_key_path = os.path.abspath(ssh_key_path) if ssh_key_path else ssh_key_path

     if ssh_local_path and os.path.isfile(ssh_local_path):
        ssh_local_path = os.path.abspath(ssh_local_path)

     elif ssh_local_path and os.path.abspath(ssh_local_path) == destination:
        ssh_local_path = os.path.abspath(ssh_local_path)


   except Exception as error:
      error_logger.error(f"Error: {str(error)}", exc_info=True)
      sys.exit(1)


   main(
    source,                    # Source path
    destination,               # Destination path
    compression,               # Compression format
    compression_level,         # Compression level 0-9
    encryption,                # Use encryption
    ssh_connection,            # SSH enabled?
    password,             # Path or loaded password
    ssh_host, ssh_port,        # SSH connection
    ssh_user, ssh_key_path,    # Auth info
    ssh_remote_path,           # Remote backup path
    ssh_local_path,            # Local copy of backup
    date_and_time,             # Timestamp
    error_logger               # Logger for errors
   )
