from cryptography.fernet import Fernet
from base64 import b64encode
import os
from typing import Optional

class Encryption:
    def __init__(self, key: Optional[str] = None):
        self.key = key or os.getenv('ENCRYPTION_KEY') or Fernet.generate_key()
        self.fernet = Fernet(self.key)
        
    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()
        
    def decrypt(self, encrypted_data: str) -> str:
        return self.fernet.decrypt(encrypted_data.encode()).decode()
        
    @staticmethod
    def generate_key() -> str:
        return b64encode(os.urandom(32)).decode() 