
WARNING: The main modules (backupx.py and decypherx.py)
must not be moved outside the BackupX directory, 
as their proper functionality depends on this location.


BackupX - Secure Automated Backup & Extraction Tool
====================================================

Version: 1.0.0
Author: J.P. Rojas
License: GPLv3
Status: Stable

Overview
--------

BackupX is a secure and automated tool for backing up and extracting encrypted archives on Linux and Windows.
It supports .zip, .7z, and .7z.aes formats, with optional AES encryption and remote SSH transfer.

Key Features
------------

- AES-256 encryption (native for .zip, optional post-encryption for .7z)
- Compression support: .zip and .7z
- Decryption of .aes files via password file
- Conflict-safe extraction with automatic renaming
- Archive content listing without extraction (--listen)
- Remote backup via SSH with key-based authentication
- Strong input validation and overflow protection
- Full logging (info + error) for auditing and debugging

Installing Dependencies
-----------------------

Installing Python 3 and pip in Linux Distributions (Debian, Ubuntu, Kali, Linux Mint, etc.)

Run the following commands in the terminal:

- sudo apt update
- sudo apt install python3 python3-pip -y


Installing Python 3 and pip in Windows:

1. Download the Python installer from:
- https://www.python.org/downloads/

2. Open the installer and check the Add Python to PATH box, then click Install Now

3. pip is automatically installed with Python since version 3.4

4. For more information about pip, you can visit:
- https://pip.pypa.io/en/stable/installation/

Manual Backup Execution
-----------------------

To run a backup manually:

    python3 backupx.py

By default, it will:

- Compress the source path defined in config.ini
- Create a backup archive like:
    - home_backup_2025-07-18.zip
    - home_backup_2025-07-18.7z
- Log the full process to info.log or error.log

Manual Extraction / Decryption
------------------------------

Use decypherx.py to extract and decrypt .zip, .7z, or .7z.aes archives:

    python3 decypherx.py -e path/to/archive.7z.aes -d path/to/key.txt -o ./restore

Other examples:

- List contents only (no extraction):

      python3 decypherx.py -e archive.zip -l

- Force overwrite instead of renaming conflicting files:

      python3 decypherx.py -e archive.zip -o ./output -f

Automating Backups
------------------

On Linux (with cron):

1. Open crontab:

       crontab -e

2. Add this line to schedule backup daily at 3:00 AM:

       0 3 * * * /usr/bin/python3 /absolute/path/to/BackupX/backupx.py >> /absolute/path/to/BackupX/backup.log 2>&1

On Windows (Task Scheduler):

1. Open Task Scheduler
2. Create a new Basic Task
3. Set a daily trigger (e.g., 3:00 AM)
4. Set the action to run:

       python C:\Path\To\BackupX\backupx.py

5. (Optional) Redirect logs:

       python C:\Path\To\BackupX\backupx.py >> C:\Path\To\BackupX\backup.log 2>&1

Logs
----

Both scripts create two log files:

- info.log â- Successful operations and key events
- error.log - Failures and error traces

Check these regularly to ensure everything is functioning properly.

Recommendations
---------------

- Run the scripts manually first to confirm proper setup.
- Ensure there's enough free space before scheduled backups.
- Use secure, plain-text password files (no raw passwords via CLI).
- Periodically move backups to external drives or cloud storage.
- Keep config.ini safe and well configured.

License
-------

This project is licensed under the GNU General Public License v3.0 (GPLv3).
You are free to use, modify, and redistribute this software under its terms.
See the LICENSE file for full legal details.
