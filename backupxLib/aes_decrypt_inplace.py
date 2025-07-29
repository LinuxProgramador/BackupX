import os
import sys
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from backupxLib.initialize_loggers import setup_loggers

error_logger, info_logger = setup_loggers()

def derive_key(password: str) -> bytes:
    """Derives a 32-byte AES-256 key using SHA-256."""
    return sha256(password.encode()).digest()

def decrypt_file(file_path: str, password: str) -> None:
    """Decrypts a .aes file in-place"""
    try:

        if not os.path.isfile(file_path):
            error_logger.error(f"[!] File not found: {file_path}")
            sys.exit(1)

        key = derive_key(password)

        with open(file_path, 'rb') as f:
            data = f.read()

        if len(data) < 16:
            error_logger.error(f"[!] Encrypted file too short or corrupted: {file_path}")
            sys.exit(1)

        iv = data[:16]
        ciphertext = data[16:]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

        # Restore original filename by removing .aes extension
        original_path = file_path[:-4] if file_path.endswith('.aes') else file_path

        with open(original_path, 'wb') as f:
            f.write(plaintext)

    except (ValueError, KeyError) as data:
        error_logger.error(f"[!] Decryption failed: incorrect password or corrupted data {str(data)}", exc_info=True)
        sys.exit(1)

    except Exception as error:
        error_logger.error(f"Unexpected error while decoding data: {str(error)}", exc_info=True)
        sys.exit(1)
