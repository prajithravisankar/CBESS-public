# AES Encryption and Decryption Using Chess Moves

This document provides an in-depth explanation of the **AES-256 encryption and decryption system** implemented using a **chess-based key generator**. The implementation consists of two core classes:

- **ChessKeyGenerator**: Converts a sequence of chess moves into a 32-byte key suitable for AES-256 encryption.
- **AESEncryptorAndDecryptor**: Handles encryption and decryption using AES in CBC (Cipher Block Chaining) mode.

## 📌 1. Imports and Dependencies

```python
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
```

### 🔹 Explanation of Imports

#### **1. `hashlib` (Python Standard Library)**
- Provides various hashing functions.
- Used here to generate a **256-bit (32-byte) key** from chess moves using **SHA-256**.
- Hashing is a one-way function, meaning it cannot be reversed to retrieve the original input.

#### **2. `cryptography.hazmat.primitives.ciphers`**
- **`Cipher`**: Creates a cipher object used for encryption and decryption.
- **`algorithms`**: Provides different encryption algorithms, such as **AES (Advanced Encryption Standard)**.
- **`modes`**: Defines different operational modes for block ciphers (e.g., **CBC, ECB, CTR**).
  - We use **CBC (Cipher Block Chaining)** mode because it's more secure than **ECB**.

#### **3. `cryptography.hazmat.backends`**
- **`default_backend()`**: Supplies the best available cryptographic implementation on the system.

#### **4. `os` (Python Standard Library)**
- **`os.urandom(16)`**: Generates a **random 16-byte Initialization Vector (IV)** to ensure security in CBC mode.

---

## 🔑 2. ChessKeyGenerator Class

```python
class ChessKeyGenerator:
    """
    Converts sequence of chess moves into a 32-byte key suitable for AES-256 encryption.
    """
    def __init__(self, moves: str):
        """
        Constructor for ChessKeyGenerator.

        :param moves: The string of chess moves to be converted into a 32-byte key.
        """
        self.moves = moves

    def generateKey(self) -> bytes:
        """
        Generates a 32-byte key suitable for AES-256 encryption.

        :return: A 32-byte SHA-256 hash derived from the chess moves.
        """
        sha256HashObject32Byte = hashlib.sha256()
        sha256HashObject32Byte.update(self.moves.encode('utf-8'))  # Convert string to bytes and hash
        return sha256HashObject32Byte.digest()[:32]  # Extract the first 32 bytes
```

### 🔹 How it Works

1. **Stores the Chess Moves**: Takes a string of chess moves as input and stores it.
2. **Hashes the Moves with SHA-256**:
   - SHA-256 always produces a **256-bit (32-byte) output**.
   - The output is **deterministic**, meaning the same input always generates the same hash.
3. **Extracts the First 32 Bytes**:
   - Since AES-256 requires exactly **32 bytes (256 bits)**, we use the full hash output.

### 🛡 Security Considerations
- The security of the encryption depends on the **complexity of the chess move sequence**.
- **Short or predictable chess moves** may lead to weak encryption keys.
- A **Key Derivation Function (KDF)** like **PBKDF2 or Argon2** could be used for better security.

---

## 🔐 3. AESEncryptorAndDecryptor Class

```python
class AESEncryptorAndDecryptor:
    """
    Handles AES-256 encryption and decryption using the CBC (Cipher Block Chaining) mode.
    """
    def __init__(self, key: bytes):
        """
        Constructor for AESEncryptorAndDecryptor.

        :param key: 32-byte AES key.
        """
        self.key = key
```

### 🔹 Class Purpose
- Manages AES encryption and decryption.
- Uses **AES-256 in CBC mode**, which requires **a 32-byte key** and **a 16-byte IV**.

---

### ⚡ 3.1 Padding Function for Block Alignment

```python
    def doPaddingHelper(self, inputString: str) -> str:
        """
        Adds PKCS7 padding to a string.

        :param inputString: Input string to be padded.
        :return: PKCS7 padded string.
        """
        blockSizeForAES = 16
        numberOfPaddingBytesNeeded = blockSizeForAES - len(inputString) % blockSizeForAES
        return inputString + chr(numberOfPaddingBytesNeeded) * numberOfPaddingBytesNeeded
```

### 🔹 Why Padding is Needed
- **AES is a block cipher** that encrypts data in **16-byte blocks**.
- **If the plaintext is not a multiple of 16**, it needs **PKCS7 padding**.
- PKCS7 padding works by **adding bytes equal to the number of missing bytes**.
  
---

### 🔥 3.2 AES Encryption Method

```python
    def encrypt(self, plainText: str) -> bytes:
        """
        Encrypts plaintext using AES-256-CBC.

        :param plainText: The string to encrypt.
        :return: Encrypted bytes (IV + ciphertext).
        """
        paddedPlainText = self.doPaddingHelper(plainText)
        paddedPlainTextToBytes = paddedPlainText.encode('utf-8')
        initializationVector = os.urandom(16)
        cipherObject = Cipher(algorithms.AES(self.key), modes.CBC(initializationVector), backend=default_backend())
        encryptorObject = cipherObject.encryptor()
        cipherText = encryptorObject.update(paddedPlainTextToBytes) + encryptorObject.finalize()
        return initializationVector + cipherText
```

### 🔹 Step-by-Step Breakdown
1. **Pads the Plaintext** using `doPaddingHelper`.
2. **Encodes it to bytes** (AES works with bytes, not strings).
3. **Generates a 16-byte IV** using `os.urandom(16)`.
4. **Initializes AES in CBC mode** with the IV.
5. **Encrypts the padded plaintext**.
6. **Returns the IV + ciphertext** (IV is needed for decryption).

---

### 🔄 3.3 AES Decryption Method

```python
    def decrypt(self, cipherText: bytes) -> str:
        """
        Decrypts ciphertext using AES-256-CBC.
        """
        initializationVector = cipherText[:16]
        actualCipherText = cipherText[16:]
        cipherObject = Cipher(algorithms.AES(self.key), modes.CBC(initializationVector), backend=default_backend())
        decryptorObject = cipherObject.decryptor()
        paddedPlainText = decryptorObject.update(actualCipherText) + decryptorObject.finalize()
        return self.removePadding(paddedPlainText).decode('utf-8')
```

### 🔹 How Decryption Works
1. **Extracts IV** from the first 16 bytes.
2. **Extracts the actual ciphertext** (remaining bytes).
3. **Initializes AES with the same key and IV**.
4. **Decrypts and removes padding**.

---

Here's a markdown file based on your code:

---

# utils.py

### 1. Imports:

```python
import chess
import chess.pgn
from PIL import Image, ImageDraw
import os
from io import StringIO
```

- **chess**: This is the Python chess library. It allows you to represent chess boards, make moves, and work with chess positions.
- **chess.pgn**: This part of the chess library deals with parsing and creating chess games in PGN (Portable Game Notation) format. PGN is a standard text format for recording chess games.
- **PIL (Pillow)**:
  - **Image**: The core module for image manipulation (creating, opening, saving, etc.).
  - **ImageDraw**: Provides drawing capabilities, allowing you to draw shapes, text, and other elements on images.
- **os**: Used here to check if the piece image files exist.
- **io.StringIO**: This is used to treat a string as a file. It's used to create a PGN "file" from the input moves string.

---

### 2. `chessPieceImages` Dictionary:

```python
chessPieceImages = {
    # Black pieces
    'r': '/path/to/r.png',
    'n': '/path/to/n.png',
    'b': '/path/to/b.png',
    'q': '/path/to/q.png',
    'k': '/path/to/k.png',
    'p': '/path/to/p.png',

    # White pieces
    'R': '/path/to/RW.png',
    'N': '/path/to/NW.png',
    'B': '/path/to/BW.png',
    'Q': '/path/to/QW.png',
    'K': '/path/to/KW.png',
    'P': '/path/to/PW.png'
}
```

**Purpose**: This dictionary maps chess piece symbols (e.g., 'r' for black rook, 'K' for white king) to the file paths of the corresponding image files. Make sure to replace `/path/to/` with your specific file paths.

**Important**: The file paths are absolute paths, meaning they are specific to your computer. If you share this code, it's advisable to use relative paths or make the paths dynamic based on the project structure.

---

### 3. `generateBoardImage(fen: str, fileName: str, squareSize=50)` Function:

```python
def generateBoardImage(FEN: str, fileName: str, squareSize=50):
    """
    Generates a chess board image with pieces in it
    :param FEN: Forsyth-Edwards Notation that represents the chess board
    :param fileName: name of the file where we will save the chess board image
    :param squareSize: size in pixel of each square in the chess board
    """
    try:
        board = chess.Board(FEN)
    except ValueError:
        board = chess.Board()
        print(f"Invalid FEN: {FEN}, since given FEN is incorrect, we are using starting position")

    img = Image.new("RGB", (8 * squareSize, 8 * squareSize))
    imageDrawObject = ImageDraw.Draw(img)

    # draw chess board
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 == 0:
                color = (240, 217, 181)
            else:
                color = (181, 136, 99)
            imageDrawObject.rectangle([
                col * squareSize,
                row * squareSize,
                (col + 1) * squareSize,
                (row + 1) * squareSize
            ], fill=color)

    # draw pieces
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            symbol = piece.symbol()
            if symbol in chessPieceImages:
                imgPath = chessPieceImages[symbol]
                if os.path.exists(imgPath):
                    x = chess.square_file(square) * squareSize
                    y = (7 - chess.square_rank(square)) * squareSize
                    try:
                        pieceImage = Image.open(imgPath).convert("RGBA").resize((squareSize, squareSize))
                        img.paste(pieceImage, (x, y), pieceImage)
                    except Exception as e:
                        print(f"Error loading {imgPath}: {str(e)}")
                else:
                    print(f"Missing Image: {imgPath}")

    img.save(fileName)
    print(f"Generated Board Image: {fileName}")
```

**Purpose**: This function generates a chessboard image based on a given FEN string.

**Arguments**:
- `FEN`: The FEN string representing the board position.
- `fileName`: The name of the file to save the generated image to.
- `squareSize`: The size (in pixels) of each square on the chessboard.

**Logic**:

1. **Board Initialization**:  
   `board = chess.Board(FEN)` initializes a chess board from the provided FEN string. If invalid, a default board is used.

2. **Image Creation**:  
   An RGB image is created with dimensions `8 * squareSize` for both width and height.

3. **Drawing the Chessboard**:  
   The nested loops iterate over the chessboard's rows and columns. Each square is drawn with alternating colors.

4. **Drawing Pieces**:  
   - Iterates through all squares on the board and checks if there’s a piece.
   - If there’s a piece, it checks for its symbol and attempts to load the corresponding image.
   - If the image exists, it resizes it to fit the square and pastes it on the image.

5. **Saving the Image**:  
   The resulting image is saved to the specified `fileName`.

---

### 4. `getGamePositions(moves: str)` Function:

```python
def getGamePositions(moves: str):
    """
    Parse moves and return list of FEN positions
    :param moves: string of moves to be parsed
    :return: FEN positions
    """
    try:
        game = chess.pgn.read_game(StringIO(f"1. {moves}"))
        board = game.board()
        positions = []

        for move in game.mainline_moves():
            board.push(move)
            positions.append(board.fen())

        return positions

    except Exception as e:
        print(f"Error parsing {moves}: {str(e)}")
        return [chess.Board().fen()]
```

**Purpose**: This function takes a string of chess moves and returns a list of FEN positions after each move.

**Arguments**:
- `moves`: A string representing the moves in PGN format.

**Logic**:
1. **Parsing the Moves**:  
   The PGN string is parsed using `chess.pgn.read_game()`. It reads the game and returns the moves in the mainline.

2. **Generating FEN Positions**:  
   For each move, the board is updated, and the FEN string representing the position is added to the list `positions`.

3. **Return**:  
   The function returns a list of FEN strings, one for each position after a move. If parsing fails, it returns the initial FEN string.

---

### Notes:
- The path to the chess piece images needs to be correctly set in `chessPieceImages`. Ideally, use relative paths for portability.
- This script requires the `Pillow` library for image manipulation and the `python-chess` library for handling chess logic.

---

```python
# =================================================IMPORT STATEMENTS====================================================
import chess
import chess.pgn
from PIL import Image, ImageDraw
import os
from io import StringIO

from chess import PIECE_SYMBOLS
# ======================================================================================================================
```

## Purpose of the Imports:
1. **chess**: A Python library to represent chess boards, make moves, and work with chess positions.
2. **chess.pgn**: Part of the chess library for parsing and creating chess games in PGN (Portable Game Notation) format.
3. **PIL (Pillow)**:
   - **Image**: Core module for image manipulation (creating, opening, saving, etc.).
   - **ImageDraw**: Provides drawing capabilities to draw shapes, text, and other elements on images.
4. **os**: Used for checking if the piece image files exist on the system.
5. **StringIO**: Allows the chess moves string to be treated as a file, which is useful for parsing PGN data.

## PIECE_IMAGES Dictionary:
```python
chessPieceImages = {
    # Black pieces
    'r': '/Users/prajithravisankar/Documents/personal/projects/python/CBESS/chessPieces/r.png',
    'n': '/Users/prajithravisankar/Documents/personal/projects/python/CBESS/chessPieces/n.png',
    'b': '/Users/prajithravisankar/Documents/personal/projects/python/CBESS/chessPieces/b.png',
    'q': '/Users/prajithravisankar/Documents/personal/projects/python/CBESS/chessPieces/q.png',
    'k': '/Users/prajithravisankar/Documents/personal/projects/python/CBESS/chessPieces/k.png',
    'p': '/Users/prajithravisankar/Documents/personal/projects/python/CBESS/chessPieces/p.png',

    # White pieces
    'R': '/Users/prajithravisankar/Documents/personal/projects/python/CBESS/chessPieces/RW.png',
    'N': '/Users/prajithravisankar/Documents/personal/projects/python/CBESS/chessPieces/NW.png',
    'B': '/Users/prajithravisankar/Documents/personal/projects/python/CBESS/chessPieces/BW.png',
    'Q': '/Users/prajithravisankar/Documents/personal/projects/python/CBESS/chessPieces/QW.png',
    'K': '/Users/prajithravisankar/Documents/personal/projects/python/CBESS/chessPieces/KW.png',
    'P': '/Users/prajithravisankar/Documents/personal/projects/python/CBESS/chessPieces/PW.png'
}
```

## Purpose:
The `chessPieceImages` dictionary maps chess piece symbols (e.g., `'r'` for black rook, `'K'` for white king) to their respective image file paths. 
- **Important**: These paths should be converted to **relative paths** for portability.

### `generateBoardImage(FEN, fileName, squareSize=50)` Function:

```python
def generateBoardImage(FEN: str, fileName: str, squareSize = 50):
    """
    Generates a chess board image with pieces in it
    :param FEN: Forsyth-Edwards Notation that represents the chess board
    example: (rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1)
    :param fileName: name of the file where we will save the chess board image
    :param squareSize: size in pixel of each square in the chess board
    """
    try:
        board = chess.Board(FEN)
    except ValueError:
        board = chess.Board()
        print(f"Invalid FEN: {FEN}, since given FEN is incorrect, we are using starting position")

    img = Image.new("RGB", (8 * squareSize, 8 * squareSize))
    imageDrawObject = ImageDraw.Draw(img)

    # Draw chess board
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 == 0:
                color = (240, 217, 181)
            else:
                color = (181, 136, 99)
            imageDrawObject.rectangle([
                col * squareSize,
                row * squareSize,
                (col + 1) * squareSize,
                (row + 1) * squareSize
            ], fill=color)

    # Draw pieces
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            symbol = piece.symbol()
            if symbol in chessPieceImages:
                imgPath = chessPieceImages[symbol]
                if os.path.exists(imgPath):
                    x = chess.square_file(square) * squareSize
                    y = (7 - chess.square_rank(square)) * squareSize
                    try:
                        pieceImage = Image.open(imgPath).convert("RGBA").resize((squareSize, squareSize))
                        img.paste(pieceImage, (x, y), pieceImage)
                    except Exception as e:
                        print(f"Error loading {imgPath}: {str(e)}")
                else:
                    print(f"Missing Image: {imgPath}")

    img.save(fileName)
    print(f"Generated Board Image: {fileName}")
```

### Purpose:
This function generates a chessboard image from a given FEN (Forsyth-Edwards Notation) string and saves the image to a file. 
- **Arguments**:
  - **FEN**: A string representing the chessboard position.
  - **fileName**: The filename where the generated image will be saved.
  - **squareSize**: The pixel size of each square on the board.

### Logic:
1. **Board Initialization**: The FEN string is parsed to initialize the chess board.
2. **Image Creation**: A blank image of the appropriate size is created, and the chessboard is drawn.
3. **Piece Drawing**: The pieces are drawn using their corresponding images from the `chessPieceImages` dictionary. 
4. **Error Handling**: If a piece image cannot be loaded, it is logged as an error.

### `getGamePositions(moves: str)` Function:

```python
def getGamePositions(moves: str):
    """
    takes a string of chess moves (in algebraic notation) and returns a list of FEN strings representing the
    board position after each move.
    :param moves: string of moves to be parsed
    :return: FEN positions
    """
    try:
        game = chess.pgn.read_game(StringIO(f"1. {moves}"))
        board = game.board()
        positions = []

        for move in game.mainline_moves():
            board.push(move)
            positions.append(board.fen())

        return positions
    except Exception as e:
        print(f"Error parsing moves: {str(e)}")
        return [chess.Board().fen()]
```

### Purpose:
This function parses a string of chess moves and returns a list of FEN strings representing the board positions after each move.

### Logic:
1. **PGN Parsing**: The string of chess moves is parsed into a PGN format.
2. **FEN Generation**: For each move, the position of the board is updated, and the corresponding FEN is added to the list.
3. **Error Handling**: If there is an error while parsing the moves or generating the FEN, the function returns the starting position.

```
```
---

# Steganography

This Python script implements basic steganography, allowing users to hide text within an image using the least significant bit (LSB) technique. The encoded image can be shared, and the hidden message can be extracted from it.

## Functions

### 1. `encode_image(image_path, message, output_image_path)`
Encodes a text message into an image and saves the result as a new image.

- **Parameters:**
  - `image_path` (str): Path to the input image file.
  - `message` (str): Text message to encode within the image.
  - `output_image_path` (str): Path where the encoded image will be saved.
  
- **Returns:**
  - None
  
- **Functionality:**
  - Opens the image and ensures the message fits within the image's pixel data.
  - Converts the message into its binary representation and embeds it in the least significant bit of the image's pixel values.
  - Saves the resulting image with the embedded message.

### 2. `decode_image(encoded_image_path)`
Decodes the hidden message from an encoded image.

- **Parameters:**
  - `encoded_image_path` (str): Path to the encoded image file.

- **Returns:**
  - (str): The hidden message.

- **Functionality:**
  - Opens the encoded image and extracts the least significant bits from the image's pixels.
  - Reconstructs the message by reading the embedded binary data and converting it back to text.

### 3. `text_to_bin(text)`
Converts a text message into its binary representation.

- **Parameters:**
  - `text` (str): The text message to convert.

- **Returns:**
  - (str): The binary string representation of the text.

- **Functionality:**
  - Iterates through each character in the text and converts it to its 8-bit binary equivalent.

### 4. `bin_to_text(binary_data)`
Converts binary data back into text.

- **Parameters:**
  - `binary_data` (str): A binary string to convert back into text.

- **Returns:**
  - (str): The decoded text message.

- **Functionality:**
  - Splits the binary data into chunks of 8 bits and converts each chunk to its corresponding character.

### 5. `get_image_pixels(image_path)`
Extracts pixel data from an image.

- **Parameters:**
  - `image_path` (str): Path to the image file.

- **Returns:**
  - (list): A list of pixels in the image.

- **Functionality:**
  - Opens the image and retrieves the pixel data as a list, where each pixel is represented by its RGB (Red, Green, Blue) values.

### 6. `set_image_pixels(image_path, new_pixels)`
Sets the modified pixel data back into the image.

- **Parameters:**
  - `image_path` (str): Path to the image file.
  - `new_pixels` (list): The new pixel data to set in the image.

- **Returns:**
  - None

- **Functionality:**
  - Opens the image and applies the new pixel data to it, saving the changes.

---