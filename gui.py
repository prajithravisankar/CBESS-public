import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import sys
import threading
import subprocess

import chess
import pyperclip
from PIL import Image, ImageTk

# Import the project modules
from encryption import ChessKeyGenerator, AESEncryptorAndDecryptor
from steganography import Steganography
from utils import generateBoardImage, getGamePositions


class CBESSApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chess-Based Encryption and Steganography System (CBESS)")
        self.geometry("1000x700")
        self.minsize(900, 650)

        # Set icon if available
        try:
            self.iconbitmap("chess_icon.ico")
        except:
            pass

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TNotebook', background='#f0f0f0')
        self.style.configure('TNotebook.Tab', padding=[20, 5], font=('Arial', 10, 'bold'))
        self.style.configure('TFrame', background='#f5f5f5')
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'), padding=10, background='#f5f5f5')
        self.style.configure('Subheader.TLabel', font=('Arial', 12, 'bold'), padding=5, background='#f5f5f5')
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('Accent.TButton', background='#4a86e8', foreground='white')
        self.style.map('Accent.TButton', background=[('active', '#619ff0')])

        # Variables
        self.chess_moves = tk.StringVar()
        self.plaintext = tk.StringVar()
        self.cipher_image_path = tk.StringVar(value="cipher_board.png")
        self.key_image_path = tk.StringVar(value="key_board.png")
        self.last_encrypted_text = None
        self.encryption_moves = None
        self.key_moves = None
        self.board = chess.Board()  # create chess board here

        # Create main container
        self.main_container = ttk.Notebook(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.encrypt_tab = ttk.Frame(self.main_container)
        self.decrypt_tab = ttk.Frame(self.main_container)
        self.about_tab = ttk.Frame(self.main_container)

        self.main_container.add(self.encrypt_tab, text="Encrypt Message")
        self.main_container.add(self.decrypt_tab, text="Decrypt Message")
        self.main_container.add(self.about_tab, text="About CBESS")

        # Build the UI components for each tab
        self._build_encrypt_tab()
        self._build_decrypt_tab()
        self._build_about_tab()

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _build_encrypt_tab(self):
        # Main layout frames
        left_frame = ttk.Frame(self.encrypt_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        right_frame = ttk.Frame(self.encrypt_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Frame Contents (Input Section)
        ttk.Label(left_frame, text="Encryption", style='Header.TLabel').pack(fill=tk.X)

        # Chess moves section
        moves_frame = ttk.LabelFrame(left_frame, text="Chess Moves (Key Source)")
        moves_frame.pack(fill=tk.X, pady=10, padx=5)

        # Add chess control buttons
        chess_buttons_frame = ttk.Frame(moves_frame)
        chess_buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(chess_buttons_frame, text="Launch Chess Game",
                   command=self.launch_chess_game).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Button(chess_buttons_frame, text="Paste Moves",
                   command=self.paste_chess_moves).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        ttk.Label(moves_frame, text="Enter or paste chess moves in algebraic notation:").pack(anchor=tk.W, padx=5,
                                                                                              pady=5)
        self.moves_text = scrolledtext.ScrolledText(moves_frame, height=5, width=40, wrap=tk.WORD)
        self.moves_text.pack(fill=tk.X, padx=5, pady=5)

        # Plaintext section
        text_frame = ttk.LabelFrame(left_frame, text="Plaintext Message")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)

        ttk.Label(text_frame, text="Enter the message you want to encrypt:").pack(anchor=tk.W, padx=5, pady=5)

        self.plaintext_text = scrolledtext.ScrolledText(text_frame, height=10, width=40, wrap=tk.WORD)
        self.plaintext_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Output paths
        paths_frame = ttk.LabelFrame(left_frame, text="Output Image Paths")
        paths_frame.pack(fill=tk.X, pady=10, padx=5)

        # Cipher image path
        cipher_frame = ttk.Frame(paths_frame)
        cipher_frame.pack(fill=tk.X, pady=5)

        ttk.Label(cipher_frame, text="Cipher Image:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(cipher_frame, textvariable=self.cipher_image_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(cipher_frame, text="Browse",
                   command=lambda: self.browse_file_path(self.cipher_image_path, save=True)).pack(side=tk.RIGHT, padx=5)

        # Key image path
        key_frame = ttk.Frame(paths_frame)
        key_frame.pack(fill=tk.X, pady=5)

        ttk.Label(key_frame, text="Key Image:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(key_frame, textvariable=self.key_image_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(key_frame, text="Browse",
                   command=lambda: self.browse_file_path(self.key_image_path, save=True)).pack(side=tk.RIGHT, padx=5)

        # Encryption & embedding button (combined process)
        ttk.Button(left_frame, text="Encrypt & Embed Message",
                   command=self.encrypt_and_embed, style='Accent.TButton').pack(fill=tk.X, pady=10, padx=5)

        # Right Frame Contents (Preview Section)
        ttk.Label(right_frame, text="Image Preview", style='Header.TLabel').pack(fill=tk.X)

        # Preview tabs
        preview_tabs = ttk.Notebook(right_frame)
        preview_tabs.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.cipher_preview_tab = ttk.Frame(preview_tabs)
        self.key_preview_tab = ttk.Frame(preview_tabs)

        preview_tabs.add(self.cipher_preview_tab, text="Cipher Board")
        preview_tabs.add(self.key_preview_tab, text="Key Board")

        # Cipher image preview
        self.cipher_preview_label = ttk.Label(self.cipher_preview_tab, text="No cipher image generated yet")
        self.cipher_preview_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Key image preview
        self.key_preview_label = ttk.Label(self.key_preview_tab, text="No key image generated yet")
        self.key_preview_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Process details frame
        details_frame = ttk.LabelFrame(right_frame, text="Process Details")
        details_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)

        self.details_text = scrolledtext.ScrolledText(details_frame, height=10, width=40, wrap=tk.WORD,
                                                      state=tk.DISABLED)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _build_decrypt_tab(self):
        # Main layout frames
        left_frame = ttk.Frame(self.decrypt_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        right_frame = ttk.Frame(self.decrypt_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Frame Contents (Input Section)
        ttk.Label(left_frame, text="Decryption", style='Header.TLabel').pack(fill=tk.X)

        # Image input section
        images_frame = ttk.LabelFrame(left_frame, text="Steganographic Images")
        images_frame.pack(fill=tk.X, pady=10, padx=5)

        # Cipher image input
        cipher_frame = ttk.Frame(images_frame)
        cipher_frame.pack(fill=tk.X, pady=5)

        self.decrypt_cipher_path = tk.StringVar()
        ttk.Label(cipher_frame, text="Cipher Image:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(cipher_frame, textvariable=self.decrypt_cipher_path).pack(side=tk.LEFT, fill=tk.X, expand=True,
                                                                            padx=5)
        ttk.Button(cipher_frame, text="Browse",
                   command=lambda: self.browse_file_path(self.decrypt_cipher_path)).pack(side=tk.RIGHT, padx=5)

        # Key image input
        key_frame = ttk.Frame(images_frame)
        key_frame.pack(fill=tk.X, pady=5)

        self.decrypt_key_path = tk.StringVar()
        ttk.Label(key_frame, text="Key Image:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(key_frame, textvariable=self.decrypt_key_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(key_frame, text="Browse",
                   command=lambda: self.browse_file_path(self.decrypt_key_path)).pack(side=tk.RIGHT, padx=5)

        # Decrypt button (combined extract & decrypt)
        ttk.Button(left_frame, text="Decrypt Message",
                   command=self.decrypt_message, style='Accent.TButton').pack(fill=tk.X, pady=10, padx=5)

        # Extracted key
        key_display_frame = ttk.LabelFrame(left_frame, text="Extracted Chess Moves (Key Source)")
        key_display_frame.pack(fill=tk.X, pady=10, padx=5)

        self.extracted_key_text = scrolledtext.ScrolledText(key_display_frame, height=5, width=40, wrap=tk.WORD,
                                                            state=tk.DISABLED)
        self.extracted_key_text.pack(fill=tk.X, padx=5, pady=5)

        # Right Frame Contents (Decrypted message)
        ttk.Label(right_frame, text="Decrypted Message", style='Header.TLabel').pack(fill=tk.X)

        # Decrypted message
        self.decrypted_text = scrolledtext.ScrolledText(right_frame, height=20, width=40, wrap=tk.WORD,
                                                        state=tk.DISABLED)
        self.decrypted_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Copy button
        ttk.Button(right_frame, text="Copy Decrypted Message",
                   command=self.copy_decrypted_message).pack(fill=tk.X, pady=10, padx=5)

    def _build_about_tab(self):
        # About Tab Contents
        ttk.Label(self.about_tab, text="Chess-Based Encryption and Steganography System",
                  style='Header.TLabel').pack(pady=20)

        about_frame = ttk.Frame(self.about_tab)
        about_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=10)

        about_text = """
        CBESS (Chess-Based Encryption and Steganography System) is a secure communication tool 
        combining cryptography and steganography using chess games as a key source.

        How it works:

        1. Encryption:
           - Play a chess game against AI and copy the moves
           - Enter a plaintext message to encrypt
           - 

        2. Key Distribution:
           - The encrypted message is embedded in a chessboard image
           - The key source (chess moves) is embedded in a second chessboard image
           - Both images can be shared through normal channels

        3. Decryption:
           - Extract the chess moves from the key image
           - Extract the ciphertext from the cipher image
           - Regenerate the same cryptographic key using the extracted chess moves
           - Decrypt the ciphertext to retrieve the original message

        This system provides secure communication without requiring a separate key exchange channel, 
        as the key is derived from the shared chess game.

        Developed by:
        Prajith Ravisankar (1302848)
        COMP-4476: Cryptography and Network Security
        """

        about_label = ttk.Label(about_frame, text=about_text, wraplength=800, justify=tk.LEFT)
        about_label.pack(fill=tk.BOTH, expand=True)

    def browse_file_path(self, var, save=False):
        """Browse for a file path and update the variable"""
        if save:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
        else:
            filepath = filedialog.askopenfilename(
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )

        if filepath:
            var.set(filepath)

    def launch_chess_game(self):
        """Launch the chess game in a separate process"""
        self.status_var.set("Launching chess game...")

        # Run in a separate thread to avoid UI freeze
        def run_chess():
            try:
                # Get the path to chessgui.py
                script_dir = os.path.dirname(os.path.abspath(__file__))
                chess_path = os.path.join(script_dir, "chessgui.py")

                # Start the chess game
                process = subprocess.Popen([sys.executable, chess_path])
                self.status_var.set("Chess game launched. Copy moves when done.")

                # Wait for the process to finish
                process.wait()
                self.status_var.set("Chess game closed.")
            except Exception as e:
                self.status_var.set(f"Error launching chess game: {str(e)}")
                messagebox.showerror("Error", f"Failed to launch chess game: {str(e)}")

        thread = threading.Thread(target=run_chess)
        thread.daemon = True
        thread.start()

    def paste_chess_moves(self):
        """Paste clipboard content to chess moves text area"""
        try:
            clipboard_content = pyperclip.paste()
            if clipboard_content:
                self.moves_text.delete(1.0, tk.END)
                self.moves_text.insert(tk.INSERT, clipboard_content)
                self.status_var.set("Chess moves pasted from clipboard.")
            else:
                self.status_var.set("Clipboard is empty.")
        except Exception as e:
            self.status_var.set(f"Error pasting from clipboard: {str(e)}")

    def encrypt_and_embed(self):
        """Combined method to encrypt and embed in one step"""
        try:
            # Get input values
            plaintext = self.plaintext_text.get(1.0, tk.END).strip()
            moves = self.moves_text.get(1.0, tk.END).strip()
            cipher_path = self.cipher_image_path.get()
            key_path = self.key_image_path.get()

            # Validate inputs
            if not moves:
                messagebox.showerror("Error", "Please enter chess moves or play a game first.")
                return

            if not plaintext:
                messagebox.showerror("Error", "Please enter a message to encrypt.")
                return

            # Split moves into two halves, but in summer we can change this to something more random
            # or based on user input for more security !!!
            move_list = moves.split()
            midpoint = len(move_list) // 2

            # First half for encryption
            encryption_moves = " ".join(move_list[:midpoint])
            # all the moves is for key embedding
            key_moves = moves  # Use all moves for key embedding

            # Store for later reference
            self.encryption_moves = encryption_moves
            self.key_moves = key_moves

            # Update details display
            self.update_details_text(
                f"Chess moves split:\n- First half for encryption: {encryption_moves}\n- Full moves for key: {key_moves}")

            # 1. Generate key from first half of chess moves
            self.status_var.set("Generating key from first half of chess moves...")
            key_generator = ChessKeyGenerator(encryption_moves)
            key = key_generator.generateKey()

            # 2. Encrypt the message
            self.status_var.set("Encrypting message...")
            encryptor = AESEncryptorAndDecryptor(key)
            cipherText = encryptor.encrypt(plaintext)
            self.last_encrypted_text = cipherText

            # 3. Generate and save cipher board image
            self.status_var.set("Generating cipher board image...")
            cipher_positions = getGamePositions(encryption_moves)
            if cipher_positions:
                last_cipher_position = cipher_positions[-1]
                generateBoardImage(last_cipher_position, cipher_path)

                # 4. Embed ciphertext in cipher image
                self.status_var.set("Embedding ciphertext in cipher image...")
                steganographer = Steganography()
                steganographer.embed(cipher_path, cipherText, cipher_path)

                # Update preview
                self.update_image_preview(cipher_path, self.cipher_preview_label)

            # 5. Generate and save key board image
            self.status_var.set("Generating key board image...")
            key_positions = getGamePositions(key_moves)
            if key_positions:
                last_key_position = key_positions[-1]
                generateBoardImage(last_key_position, key_path)

                # 6. Embed key source in key image
                self.status_var.set("Embedding key source in key image...")
                steganographer = Steganography()
                steganographer.embed(key_path, key_moves.encode('utf-8'), key_path)

                # Update preview
                self.update_image_preview(key_path, self.key_preview_label)

            self.status_var.set("Message encrypted and embedded successfully.")
            messagebox.showinfo("Success",
                                "Message encrypted and embedded successfully!\n\n"
                                "Key image contains all chess moves.\n"
                                "Cipher image contains the encrypted message.\n\n"
                                "Both images are needed for decryption.")

            # Update details with final info
            self.append_details_text("\nProcess completed successfully:"
                                     f"\n- Cipher image saved to: {cipher_path}"
                                     f"\n- Key image saved to: {key_path}")

        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))

    def update_details_text(self, text):
        """Update the details text widget with new content"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.INSERT, text)
        self.details_text.config(state=tk.DISABLED)
        self.update()  # Force UI update

    def append_details_text(self, text):
        """Append text to the details text widget"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.insert(tk.END, text)
        self.details_text.config(state=tk.DISABLED)
        self.update()  # Force UI update

    def decrypt_message(self):
        """Extract data and decrypt the message"""
        try:
            cipher_path = self.decrypt_cipher_path.get()
            key_path = self.decrypt_key_path.get()

            if not cipher_path or not os.path.exists(cipher_path):
                messagebox.showerror("Error", "Please select a valid cipher image file.")
                return

            if not key_path or not os.path.exists(key_path):
                messagebox.showerror("Error", "Please select a valid key image file.")
                return

            # 1. Extract the chess moves (key source)
            self.status_var.set("Extracting key source from key image...")
            steganographer = Steganography()
            extracted_data = steganographer.extract(key_path)
            extracted_moves = extracted_data.decode('utf-8')

            # Display the extracted moves
            self.extracted_key_text.config(state=tk.NORMAL)
            self.extracted_key_text.delete(1.0, tk.END)
            self.extracted_key_text.insert(tk.INSERT, extracted_moves)
            self.extracted_key_text.config(state=tk.DISABLED)

            # For decryption, use first half of extracted moves
            move_list = extracted_moves.split()
            midpoint = len(move_list) // 2
            decryption_moves = " ".join(move_list[:midpoint])

            # 2. Extract the ciphertext
            self.status_var.set("Extracting ciphertext from cipher image...")
            ciphertext = steganographer.extract(cipher_path)

            # 3. Generate key from first half of chess moves
            self.status_var.set("Generating key from first half of chess moves...")
            key_generator = ChessKeyGenerator(decryption_moves)
            key = key_generator.generateKey()

            # 4. Decrypt the message
            self.status_var.set("Decrypting message...")
            encryptor = AESEncryptorAndDecryptor(key)
            plaintext = encryptor.decrypt(ciphertext)

            # Display the decrypted message
            self.decrypted_text.config(state=tk.NORMAL)
            self.decrypted_text.delete(1.0, tk.END)
            self.decrypted_text.insert(tk.INSERT, plaintext)
            self.decrypted_text.config(state=tk.DISABLED)

            self.status_var.set("Message decrypted successfully.")
            messagebox.showinfo("Success", "Message decrypted successfully!")

        except Exception as e:
            self.status_var.set(f"Decryption error: {str(e)}")
            messagebox.showerror("Decryption Error", str(e))

    def copy_decrypted_message(self):
        """Copy decrypted message to clipboard"""
        try:
            message = self.decrypted_text.get(1.0, tk.END).strip()
            if message:
                pyperclip.copy(message)
                self.status_var.set("Decrypted message copied to clipboard.")
                messagebox.showinfo("Copied", "Decrypted message copied to clipboard.")
            else:
                self.status_var.set("No decrypted message to copy.")
        except Exception as e:
            self.status_var.set(f"Error copying to clipboard: {str(e)}")

    def update_image_preview(self, image_path, label_widget):
        """Update the image preview in the given label widget"""
        try:
            if os.path.exists(image_path):
                # Load and resize the image
                img = Image.open(image_path)
                max_size = 250
                ratio = min(max_size / img.width, max_size / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)

                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)

                # Update label
                label_widget.config(
                    image=photo,
                    text="",
                    compound=tk.CENTER
                )
                label_widget.image = photo
            else:
                label_widget.config(
                    image="",  # Clear the image
                    text="Image not found",
                    compound=tk.CENTER
                )
        except Exception as e:
            label_widget.config(text=f"Error loading image: {str(e)}")

    def _validate_moves(self, moves: str) -> bool:
        """Validate if chess moves are in algebraic notation."""
        try:
            # Use utils.get_game_positions to check if moves are valid
            positions = getGamePositions(moves)
            # Valid moves will have more than 1 FEN position (starting + at least 1 move)
            return len(positions) > 1
        except:
            return False


if __name__ == "__main__":
    app = CBESSApplication()
    app.mainloop()