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
    does encryption and decryption using AES algorithms
    """
    def __init__(self, key: bytes):
        """
        constructor for AESEncryptorAndDecryptor, takes 32 bytes AES key and stores it in self.key
        :param key: 32 byte AES key to use
        """
        self.key = key

    def doPaddingHelper(self, inputString: str) -> str:
        """
        PKCS7 padding helper
        :param inputString:input string to be converted to PKCS7 padding
        :return: PKCS7 padded bytes
        "abc" → "abc\x0f\x0f...\x0f" (16-byte block).
        """
        blockSizeForAES = 16
        numberOfPaddingBytesNeeded = blockSizeForAES - len(inputString) % blockSizeForAES
        return inputString + chr(numberOfPaddingBytesNeeded) * numberOfPaddingBytesNeeded


    def encrypt(self, plainText: str) -> bytes:
        """
        Encrypts plaintext using AES-CBC (cipher blockchain)
        :param plainText: string to encrypt
        :return: encrypted bytes
        """
        paddedPlainText = self.doPaddingHelper(plainText)
        paddedPlainTextToBytes = paddedPlainText.encode('utf-8')
        initializationVector = os.urandom(16)
        cipherObject = Cipher(algorithms.AES(self.key), modes.CBC(initializationVector), backend=default_backend())
        encryptorObject = cipherObject.encryptor()
        cipherText = encryptorObject.update(paddedPlainTextToBytes) + encryptorObject.finalize()
        return initializationVector + cipherText

    def removePadding(self, inputBytes: bytes) -> bytes:
        """
        Removes PKCS7 padding from decrypted binary data.
        :param inputBytes: string to remove PKCS7 padding
        :return: unpadded bytes
        """
        paddingLength = inputBytes[-1]
        return inputBytes[:-paddingLength]


    def decrypt(self, cipherText: bytes) -> bytes:
        """
        decrypts cipher text using AES-CBC (cipher blockchain)
        :param cipherText: cipher text in bytes to be decrypted
        :return:  plaintext string
        """
        initializationVector = cipherText[:16]
        actualCipherText = cipherText[16:]
        cipherObject = Cipher(algorithms.AES(self.key), modes.CBC(initializationVector), backend=default_backend())
        decryptorObject = cipherObject.decryptor()
        paddedPlainText = decryptorObject.update(actualCipherText) + decryptorObject.finalize()
        return self.removePadding(paddedPlainText).decode('utf-8')
# ============================================================CLASSES===================================================