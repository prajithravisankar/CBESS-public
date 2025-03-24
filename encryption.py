'''
NOTES:

hashlib: This module provides various hashing algorithms, including SHA-256, which is used to generate the encryption
key from the chess moves. Hashing is a one-way function: you can't easily reverse it to get the original input.
It produces a fixed-size output (in this case, 256 bits or 32 bytes for SHA-256).

cryptography.hazmat...: This is a powerful and recommended Python library for cryptography.

Cipher: Provides a way to create a cipher object that you can use to encrypt and decrypt data.

algorithms: Contains implementations of various encryption algorithms, such as AES (Advanced Encryption Standard).

modes: Defines different modes of operation for block ciphers like AES (e.g., CBC, CTR, ECB). CBC
(Cipher Block Chaining) is generally preferred over ECB because it XORs the previous ciphertext block with the current
plaintext block before encryption, making it more resistant to certain attacks.

default_backend: Provides a backend for the cryptography library, which allows it to use the best available
cryptographic implementation on your system.

os: This module provides functions for interacting with the operating system. Here, it's used for generating random
numbers (specifically, the Initialization Vector or IV).

__init__(self, moves: str): This is the constructor. It takes the chess moves as a string (moves) and stores them in
the self.moves instance variable.

generate_key(self) -> bytes: This method performs the key generation:
sha256 = hashlib.sha256(): Creates a SHA-256 hash object.
sha256.update(self.moves.encode('utf-8')): Updates the hash object with the chess moves. encode('utf-8') converts the
string of chess moves into bytes, which is what the hashing function requires.
return sha256.digest()[:32]: Calculates the SHA-256 hash digest (a sequence of bytes) and returns the first 32 bytes.
SHA-256 produces a 32-byte (256-bit) hash, and AES-256 requires a 32-byte key
'''

# =================================================IMPORT STATEMENTS====================================================
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os


# ======================================================================================================================


# ============================================================CLASSES===================================================
class ChessKeyGenerator:
    """
    Converts sequence of chess moves into 32 byte key suitable for AES-256 encryption
    """
    def __init__(self, moves: str):
        """
        this constructor takes chess moves as string and stores them in self.moves instance variable
        :param moves: The string of chess moves to be converted to 32 byte key
        """
        self.moves = moves

    def generateKey(self) -> bytes:
        """
        this method generates a 32 byte key suitable for AES-256 encryption
        :return: a 32 byte SHA-256 hash suitable for AES-256 32 byte key
        """
        sha256HashObject32Byte = hashlib.sha256()
        sha256HashObject32Byte.update(self.moves.encode('utf-8')) # string -> bytes -> feeds the byte for hashing
        return sha256HashObject32Byte.digest()[:32]


class AESEncryptorAndDecryptor:
    """

    """