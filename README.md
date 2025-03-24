# Chess-Based Encryption and Steganography System (CBESS)

## Overview

CBESS (Chess-Based Encryption and Steganography System) is a secure communication tool that combines cryptography and steganography using chess games as a key source. It provides a way to encrypt a message and hide both the encrypted message and the key within chessboard images, allowing for discreet and secure information transfer without relying on traditional, vulnerable key exchange methods.

## Problem Solved

CBESS addresses the challenge of secure key exchange in traditional encryption systems. Traditional methods often require transmitting encryption keys through separate channels, which can be intercepted. CBESS solves this by:

*   **Eliminating Traditional Key Exchange:** The key is derived from a shared chess game, so there's no need to explicitly transmit a key.
*   **Combining Encryption and Steganography:**  The encrypted message and the key source (chess moves) are hidden within images, making the communication less conspicuous.

## How It Works

CBESS operates in two main phases: Encryption/Embedding and Extraction/Decryption.

### 1. Encryption and Embedding

This phase involves the following steps:

1.  **Plaintext Input:** The user enters the message they want to encrypt.

2.  **Chess Game (Key Source):** The user plays a chess game (or enters a sequence of moves in algebraic notation).  The application supports launching a simple chess game GUI to facilitate this.

3.  **Key Generation:** The chess moves are used to generate a 32-byte AES encryption key using the SHA-256 hashing algorithm.

4.  **Encryption:**  The plaintext message is encrypted using the AES-256-CBC algorithm with the generated key.

5.  **Image Generation:** Two chessboard images are generated using the Python `chess` and `PIL` libraries:
    *   **Cipher Board:** An image of the chessboard at a position reached mid-game (approximately halfway through the entered chess moves) is created.
    *   **Key Board:**  An image of the chessboard at the *final* position of the chess game (after all moves have been played) is created.

6.  **Steganography (Embedding):**
    *   The **ciphertext** (encrypted message) is embedded into the **Cipher Board** image using Least Significant Bit (LSB) steganography.
    *   The **key source** (the sequence of chess moves) is embedded into the **Key Board** image using LSB steganography.

### 2. Extraction and Decryption

This phase reverses the process:

1.  **Image Input:** The user provides the two chessboard images (Cipher Board and Key Board).

2.  **Steganography (Extraction):**
    *   The **ciphertext** is extracted from the **Cipher Board** image.
    *   The **key source** (chess moves) is extracted from the **Key Board** image.

3.  **Key Re-generation:** The AES encryption key is re-generated from the extracted chess moves using the same SHA-256 hashing algorithm used during encryption.

4.  **Decryption:** The ciphertext is decrypted using the AES-256-CBC algorithm with the re-generated key, revealing the original message.

## Why Two Images? (Cipher Board and Key Board)

CBESS uses two chessboard images for the following reasons:

*   **Separation of Concerns:** Separating the ciphertext and the key source into two images provides an additional layer of security. If an attacker only discovers one image, they won't have both the encrypted message and the key needed to decrypt it.
*   **Different Embedding Requirements:** The ciphertext and the key source might have different size requirements.  Using two images allows you to tailor the image size to the amount of data being hidden.
*   **Plausible Deniability:** The two images can be presented as separate, unrelated chess-related images, further obscuring the true purpose.

## Advantages of CBESS

*   **Secure Communication without Key Exchange:**  The key is derived from a shared chess game, eliminating the need for a vulnerable key exchange channel.
*   **Steganographic Security:** Hiding the message and key within images makes the communication less conspicuous than traditional encryption.
*   **Easy to Use:** The system provides a user-friendly GUI for encryption, embedding, extraction, and decryption.

## Components

The system consists of the following modules:

*   **`gui.py`:** The main application file containing the Tkinter GUI.
*   **`encryption.py`:** Contains the `ChessKeyGenerator` and `AESEncryptorAndDecryptor` classes for key generation and AES encryption/decryption.
*   **`steganography.py`:** Contains the `Steganography` class for embedding and extracting data in images using LSB steganography.
*   **`utils.py`:** Contains utility functions for generating chessboard images from FEN notation (`generateBoardImage`) and parsing chess moves (`getGamePositions`).
*   **`chessgui.py`:** A separate Pygame-based GUI for playing a chess game against Stockfish and generating chess moves.
*   **`main.py`:** A command-line interface for encrypting, embedding, extracting and decrypting.

## Installation and Usage

### Prerequisites

*   **Python 3.x:**  Make sure you have Python 3 installed on your system.
*   **Libraries:** Install the required Python libraries using `pip`:
    ```bash
    pip install Pillow pygame python-chess cryptography pyperclip
    ```
*   **Stockfish:**  The chess game GUI requires the Stockfish chess engine. Download it from [https://stockfishchess.org/](https://stockfishchess.org/) and ensure it's in your system's PATH (or provide the path to the executable in `chessgui.py`).

### Installation Steps

1.  **Download the CBESS package:** Download the CBESS project files (e.g., from a zip archive or a Git repository).
2.  **Create a Virtual Environment (Recommended):** Create a Python virtual environment to isolate the project dependencies:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Linux/macOS
    .venv\Scripts\activate  # On Windows
    ```
3.  **Install Dependencies:** Install the required Python libraries using `pip` within the virtual environment (if you didn't do it already):
    ```bash
    pip install Pillow pygame python-chess cryptography pyperclip
    ```
4.  **Chess Piece Images:**
    *   Create a directory named `chessPieces` in the same directory as `chessgui.py` and `utils.py`.
    *   Place the chess piece images (e.g., `p.png`, `r.png`, `PW.png`, `RW.png`, etc.) into the `chessPieces` directory.
    *   It's *critical* that the paths in `utils.py` are correct.

### Running CBESS

**Graphical User Interface (GUI)**

1.  Navigate to the directory containing `gui4.py` (or `gui.py`).
2.  Run the GUI application:
    ```bash
    python gui.py
    ```

**Command-Line Interface (CLI)**

1.  Navigate to the directory containing `main.py`.
2.  Run the CLI application:
    ```bash
    python main.py
    ```

## Future Improvements

*   **More Robust Steganography:** Explore more advanced steganographic techniques that are more resistant to detection (e.g., Discrete Cosine Transform-based methods, adaptive embedding).
*   **Key Derivation Function (KDF):** Implement a key derivation function (e.g., PBKDF2, Argon2) to strengthen the encryption key and make it more resistant to brute-force attacks.
*   **Error Correction:** Add error correction coding to the embedded data to improve resilience against image corruption or modifications.
*   **PNG Format Validation:** Add checks to ensure the input images are PNG files in steganography.py, and potentially in utils.py
*   **Adaptive Image Size:** Implement logic to automatically adjust the size of the chessboard images based on the amount of data being embedded.
*   **Improved Key Splitting:** A better strategy to split the key from chess moves. A portion of the moves should be used for encryption key generation and a *different* portion for embedding as the key source in the key image.