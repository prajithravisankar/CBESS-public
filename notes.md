```md
# Understanding `encryption.py` - Step by Step Breakdown

## 1. Imports
```python
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
```

### **What Each Import Does:**
- **`hashlib`**: Provides hashing algorithms like SHA-256, which is used to generate the encryption key from chess moves.
- **`cryptography.hazmat...`**: A powerful library for encryption and decryption.
  - `Cipher`: Creates cipher objects for encryption/decryption.
  - `algorithms`: Provides encryption algorithms (AES, etc.).
  - `modes`: Defines block cipher modes like CBC (Cipher Block Chaining).
  - `default_backend`: Uses the best available cryptographic implementation.
- **`os`**: Used for system-related operations, such as generating random numbers for IV (Initialization Vector).

---

## 2. `ChessKeyGenerator` Class
```python
class ChessKeyGenerator:
    def __init__(self, moves: str):
        self.moves = moves

    def generate_key(self) -> bytes:
        """
        Generates a 32-byte AES-256 key by hashing chess moves with SHA-256.
        """
        sha256 = hashlib.sha256()
        sha256.update(self.moves.encode('utf-8'))
        return sha256.digest()[:32]  # Use first 32 bytes for AES-256
```
### **What This Class Does:**
- Converts chess move sequences into a **32-byte encryption key**.
- Uses SHA-256 hashing to generate the key.

### **How It Works:**
1. **Constructor (`__init__`)**: Stores the chess moves string.
2. **`generate_key` Method**:
   - Creates a SHA-256 hash object.
   - Hashes the chess moves (converted to bytes).
   - Extracts the first **32 bytes** from the hash (since AES-256 requires a 32-byte key).

---

## 3. `AESEncryptor` Class
```python
class AESEncryptor:
    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, plaintext: str) -> bytes:
        """
        Encrypts plaintext with AES-256-CBC.
        Returns IV + ciphertext (for decryption).
        """
        padded_plaintext = self._pad(plaintext)
        padded_data = padded_plaintext.encode('utf-8')
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return iv + ciphertext  # Prepend IV for decryption
```
### **How Encryption Works:**
1. **Pads the plaintext** (PKCS7 padding).
2. **Encodes it to bytes**.
3. **Generates a random 16-byte IV**.
4. **Creates AES-256 cipher** in CBC mode using the key & IV.
5. **Encrypts the data**.
6. **Returns IV + ciphertext** (IV is needed for decryption).

---

## 4. Decryption
```python
    def decrypt(self, ciphertext: bytes) -> str:
        """
        Decrypts ciphertext using AES-256-CBC.
        """
        iv = ciphertext[:16]
        actual_ciphertext = ciphertext[16:]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
        return self._unpad(padded_plaintext).decode('utf-8')
```
### **How Decryption Works:**
1. **Extracts the IV** (first 16 bytes of ciphertext).
2. **Gets the actual ciphertext**.
3. **Recreates AES-256 cipher** using the same key & extracted IV.
4. **Decrypts the ciphertext**.
5. **Removes padding** and converts it back to a string.

---

## 5. PKCS7 Padding Functions
```python
    def _pad(self, s: str) -> str:
        """
        PKCS7 padding for strings.
        """
        block_size = 16
        padding_length = block_size - len(s) % block_size
        return s + chr(padding_length) * padding_length

    def _unpad(self, s: bytes) -> bytes:
        """
        Removes PKCS7 padding.
        """
        padding_length = s[-1]  # Last byte indicates padding length
        return s[:-padding_length]
```
### **Why Padding is Needed:**
- AES is a **block cipher** (works in **16-byte blocks**).
- If the text length isn't a multiple of 16, **padding is added**.
- `_pad` adds extra bytes; `_unpad` removes them during decryption.

---
