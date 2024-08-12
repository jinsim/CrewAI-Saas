import base64
import os

from cryptography.fernet import Fernet

from cryptography.fernet import Fernet
import os


class CryptographyUtils:
    def __init__(self):
        api_encryption_key = os.getenv("API_ENCRYPTION_KEY")
        if not api_encryption_key:
            raise ValueError("API_ENCRYPTION_KEY environment variable is not set")

        self.cipher_suite = Fernet(api_encryption_key)

    def encrypt(self, value: str) -> str:
        byte_value =  self.cipher_suite.encrypt(value.encode())
        return base64.b64encode(byte_value).decode('utf-8')

    def decrypt(self, value: str) -> str:
        decoded_value = base64.b64decode(value).decode('utf-8')
        return self.cipher_suite.decrypt(decoded_value).decode()

utils = CryptographyUtils()