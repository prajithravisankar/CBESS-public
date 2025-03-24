# =================================================IMPORT STATEMENTS====================================================
import re
from encryption import ChessKeyGenerator, AESEncryptorAndDecryptor
from steganography import Steganography
from utils import generateBoardImage, getGamePositions
# ======================================================================================================================

# Global variable to hold plaintext
plaintext_global = ""


def parseMoveList(moves: str) -> str:
    """
    parses the string and removes the number in the string
    :param moves: string to parse
    :return: parsed moves
    """
    parsed = re.sub(r'\d+\.\s*', '', moves)
    return parsed.strip()


def inputMoveList() -> str:
    """
    takes input the list of chess moves
    :return: the list of chess moves entered
    """
    print("Paste your full chess move list (e.g., from https://theweekinchess.com/ or https://www.pgnmentor.com/files.html):")
    return input().strip()


def formatMoves(moveList: list, maxPlies: int) -> str:
    """
    Format moves into algebraic notation with move numbers
    :param moveList: list of moves
    :param maxPlies: max number of moves to display
    :return: a string with move numbers formatted and moves in algebraic notation
    """
    formatted = []
    moveNumber = 1
    i = 0
    while i < maxPlies and i < len(moveList):
        if i + 1 < len(moveList):
            formatted.append(f"{moveNumber}. {moveList[i]} {moveList[i + 1]}")
            i += 2
        else:
            formatted.append(f"{moveNumber}. {moveList[i]}")
            i += 1
        moveNumber += 1
    return "\n".join(formatted)


def encryptAndEmbed():
    """
    encrypts the plaintext and embed into key and cipher image
    """
    global plaintext_global

    plaintext = input("Enter the plaintext message to encrypt: ").strip()
    plaintext_global = plaintext

    fullMoveList = inputMoveList()
    parsedMoves = parseMoveList(fullMoveList)
    print(f"\nParsed key source: {parsedMoves}\n")

    positions = getGamePositions(parsedMoves)
    if not positions:
        print("Error: No valid positions generated!")
        return

    midGameIdx = len(positions) // 2
    totalPlies = len(positions)
    print(f"\nGenerating midgame board ({midGameIdx + 1}/{totalPlies} plies)")

    # Display midgame moves in algebraic notation
    moveList = parsedMoves.split()
    midGameMoves = formatMoves(moveList, midGameIdx + 1)
    print("\nMidgame Position Moves:")
    print(midGameMoves)
    print()

    generateBoardImage(positions[midGameIdx], "cipher_board.png")
    generateBoardImage(positions[-1], "key_board.png")

    keyGen = ChessKeyGenerator(parsedMoves)
    aesKey = keyGen.generateKey()
    encryptor = AESEncryptorAndDecryptor(aesKey)
    cipherText = encryptor.encrypt(plaintext)

    stego = Steganography()
    stego.embed("cipher_board.png", cipherText, "cipher_board.png")
    stego.embed("key_board.png", parsedMoves.encode('utf-8'), "key_board.png")

    print("\nEncryption complete!")
    print("- Ciphertext embedded in cipher_board.png")
    print("- Key source embedded in key_board.png\n")


def extractAndDecrypt():
    """
    extracts and decrypts data from key and cipher image
    """
    print("\n--- Decryption Process ---")
    stego = Steganography()

    try:
        extractedKeySource = stego.extract("key_board.png").decode('utf-8')
        print(f"Extracted key source: {extractedKeySource}")

        keyGen = ChessKeyGenerator(extractedKeySource)
        aesKey = keyGen.generateKey()
        #print(f"Reconstructed AES key: {aesKey.hex()}")

        extractedCipherText = stego.extract("cipher_board.png")
        #print(f"Extracted ciphertext: {extractedCipherText.hex()}")

        decryptor = AESEncryptorAndDecryptor(aesKey)
        decryptedText = decryptor.decrypt(extractedCipherText)
        print(f"Decrypted plaintext: '{decryptedText}'")

        global plaintext_global
        if decryptedText != plaintext_global and decryptedText != plaintext_global.strip():
            raise ValueError("Decryption mismatch!")
        print("\nDecryption successful!")
    except Exception as e:
        print(f"\nDECRYPTION FAILED: {str(e)}")
        raise


if __name__ == "__main__":
    print("=== CBESS Terminal Workflow ===\n")
    encryptAndEmbed()
    extractAndDecrypt()