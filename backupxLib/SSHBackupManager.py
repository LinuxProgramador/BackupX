import os
import sys
import posixpath
import paramiko
from backupxLib.initialize_loggers import setup_loggers

error_logger, info_logger = setup_loggers()


def is_valid_backup(file_path: str) -> bool:
    """Return True if file has a .zip or .7z extension (case-insensitive)"""
    return file_path.lower().endswith(('.zip', '.7z', '.7z.aes'))


def create_ssh_client(hostname: str, port: int, username: str, key_file: str) -> 'paramiko.SSHClient':
    """Connects to an SSH server using RSA key and returns the SSH client"""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key = paramiko.RSAKey.from_private_key_file(key_file)
        client.connect(hostname, port=port, username=username, pkey=private_key)
        info_logger.info(f"SSH connection established with {hostname}")
        return client
    except Exception as error:
        error_logger.error(f"SSH connection failed: {str(error)}", exc_info=True)
        sys.exit(1)


def ensure_remote_directory(sftp: 'paramiko.SFTPClient', remote_path: str) -> None:
    """Ensure all directories in the remote path exist, creating them if needed"""
    remote_dir = posixpath.dirname(remote_path)
    parts = remote_dir.split('/')
    current = ""
    for part in parts:
        if not part:
            continue
        current = current + '/' + part
        try:
            sftp.stat(current)
        except FileNotFoundError:
            try:
                sftp.mkdir(current)
                info_logger.info(f"Created remote directory: {current}")
            except Exception as error:
                error_logger.error(f"Failed to create directory {current}: {str(error)}", exc_info=True)
                sys.exit(1)


def transfer_backup(ssh_client: 'paramiko.SSHClient', local_path: str, remote_path: str) -> None:
    """Transfer a valid local backup file to the remote server via SFTP"""
    try:
        if not os.path.exists(local_path):
            error_logger.error(f"Backup file not found: {local_path}")
            sys.exit(1)

        if not is_valid_backup(local_path):
            error_logger.error("Invalid file type. Only .zip and .7z backups are allowed.")
            sys.exit(1)

        sftp = ssh_client.open_sftp()

        # If remote_path is a remote directory, add the file name
        try:
            if sftp.stat(remote_path).st_mode & 0o40000:
                remote_path = posixpath.join(remote_path, os.path.basename(local_path))
        except FileNotFoundError:
            ensure_remote_directory(sftp, remote_path)

        ensure_remote_directory(sftp, remote_path)
        sftp.put(local_path, remote_path)
        sftp.close()

        info_logger.info(f"Backup {local_path} transferred to {remote_path} via SFTP")

    except Exception as error:
        error_logger.error(f"Backup transfer failed: {str(error)}", exc_info=True)
        sys.exit(1)
