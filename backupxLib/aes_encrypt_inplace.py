import os
import sys
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from backupxLib.initialize_loggers import setup_loggers

error_logger, info_logger = setup_loggers()

def derive_key(password: str) -> bytes:
    """Derives a 32-byte AES-256 key using SHA-256."""
    return sha256(password.encode()).digest()

def encrypt_file(file_path: str, password: str) -> None:
    """Encrypts the file in-place,  using AES-256 CBC."""
    try:

      if not os.path.isfile(file_path):
         error_logger.error(f"[!] File not found: {file_path}")
         sys.exit(1)

      key = derive_key(password)
      iv = os.urandom(16)

      with open(file_path, 'rb') as f:
         plaintext = f.read()

      padded_data = pad(plaintext, AES.block_size)
      cipher = AES.new(key, AES.MODE_CBC, iv)
      ciphertext = cipher.encrypt(padded_data)
      file_path = file_path + ".aes"

      with open(file_path, 'wb') as f:
         f.write(iv + ciphertext)

    except Exception as error:
        error_logger.error(f"Unexpected error while encoding data: {str(error)}", exc_info=True)
        sys.exit(1)




