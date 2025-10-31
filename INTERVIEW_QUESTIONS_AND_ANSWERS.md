# CBESS Project - Interview Questions and Answers

## Easy Level Questions (1-5)

### 1. Can you tell me about your CBESS project? What does it do?

**Answer:** Sure! CBESS stands for Chess-Based Encryption and Steganography System. It's a secure communication tool I built that combines cryptography and steganography using chess games as a unique key source. The main idea is to encrypt a message using a key derived from chess moves, and then hide both the encrypted message and the key source within chessboard images.

What makes it interesting is that it eliminates the traditional key exchange problem in encryption. Instead of having to securely transmit an encryption key through a separate channel, both the sender and receiver just need to know the same chess game. The key is derived from those chess moves, so there's no vulnerable key exchange step. Plus, by hiding everything in innocent-looking chessboard images, the communication is much less conspicuous than sending encrypted text directly.

---

### 2. Why did you choose to use chess moves as the basis for encryption keys?

**Answer:** That's actually one of the core innovations of this project. Traditional encryption systems have this inherent vulnerability in key exchange - you need to somehow securely transmit the encryption key to the receiver, which creates a catch-22 situation.

I chose chess moves because they provide a shared secret that both parties can know without ever transmitting the key itself. If you and I both know a specific chess game - maybe a famous historical game, or one we played together - we can independently derive the same encryption key from those moves.

The chess moves also provide enough entropy for strong cryptographic keys. A typical chess game has dozens of moves with many possible variations, which when hashed, creates a sufficiently random 32-byte key for AES-256 encryption. Plus, it's a natural, memorable way to share a secret - "Remember that game we played last week?" is much more discreet than exchanging strings of random characters.

---

### 3. What is steganography and how does your project use it?

**Answer:** Steganography is the practice of hiding information within other, innocent-looking data - it's different from encryption because encryption scrambles data to make it unreadable, while steganography hides the very existence of the data.

In my project, I implemented LSB steganography - Least Significant Bit steganography. This works by modifying the least significant bits of pixel values in an image. An image is made up of pixels, and each pixel has RGB color values from 0-255. Changing the last bit of these values creates imperceptible changes to the human eye - like changing 255 to 254 - but you can store data in these bits.

My system generates two chessboard images: the cipher board embeds the encrypted message, and the key board embeds the chess moves themselves. What's clever about this approach is that even if someone intercepts one of the images, they won't have both pieces needed to decrypt the message. The images just look like normal chessboard diagrams, so there's plausible deniability.

---

### 4. What programming languages and libraries did you use, and why?

**Answer:** I built this entirely in Python, which was a deliberate choice for several reasons. Python has excellent libraries for the different components I needed - cryptography, image processing, and chess logic.

For the cryptography, I used the `cryptography` library which provides industrial-strength AES encryption with proper implementations of AES-256-CBC mode. I also used Python's built-in `hashlib` for SHA-256 hashing to convert chess moves into the 32-byte encryption key.

For image manipulation and steganography, I used PIL (Python Imaging Library) and NumPy. PIL makes it easy to open, modify, and save images, while NumPy's array operations let me efficiently manipulate pixel values for the LSB steganography implementation.

The `python-chess` library was crucial for validating chess moves, generating board positions in FEN notation, and parsing PGN format chess games. This saved me from having to implement chess logic from scratch.

For the GUI, I used Tkinter for the main application interface and Pygame for the interactive chess game component. I also integrated Stockfish, a powerful chess engine, so users could actually play a chess game to generate their moves if they wanted.

---

### 5. Can you walk me through how a user would encrypt and send a message using your system?

**Answer:** Absolutely. The workflow is actually quite straightforward from a user perspective, though there's a lot happening behind the scenes.

First, the user enters their plaintext message - whatever secret message they want to send. Then, they either play a chess game using the built-in GUI or paste in a list of chess moves in algebraic notation from an existing game. They could use a famous historical game or play one themselves.

Once they have the moves, my system generates a 32-byte AES key by taking all those moves as a string and running them through SHA-256 hashing. This key is then used to encrypt the message using AES-256 in CBC mode, which includes generating a random initialization vector for additional security.

Next, the system generates two chessboard images. The first, the cipher board, shows the board position at approximately the midpoint of the game. The second, the key board, shows the final position after all moves. Then the magic happens - the encrypted message gets embedded into the cipher board using LSB steganography, and the chess moves themselves get embedded into the key board.

The user ends up with two PNG images that look like normal chessboard diagrams. They send both images to the receiver through any channel - email, messaging apps, whatever. The receiver uses the extraction function to pull out the hidden data and decrypt the message. It's elegant because the actual communication channel doesn't need to be secure - the security is baked into the cryptography and steganography.

---

## Medium Level Questions (6-10)

### 6. Why did you choose to use two separate images instead of embedding everything in one?

**Answer:** This was actually a security design decision I made after thinking through various attack scenarios. Using two images provides several key advantages.

First is separation of concerns and defense in depth. If an attacker somehow discovers or intercepts only one of the images, they're still missing a critical piece of the puzzle. With just the cipher board, they have the encrypted message but no way to derive the key. With just the key board, they have the chess moves but nothing to decrypt. You need both images to successfully decrypt the message, which essentially creates a two-factor security system.

Second is capacity management. The encrypted message and the chess move list can have very different sizes. Splitting them into separate images gives me flexibility - I can generate appropriately sized images for each payload without one being unnecessarily large.

Third is plausible deniability. Two separate chessboard images at different positions in a game look like innocuous chess study materials or position diagrams. Someone analyzing the images wouldn't necessarily connect them. You could even send them through different channels or at different times to reduce suspicion.

From an implementation standpoint, it also made the code more modular and easier to maintain. Each image has a single, well-defined purpose, which follows good software engineering principles.

---

### 7. Explain your implementation of AES encryption. Why did you choose AES-256-CBC mode?

**Answer:** I implemented AES encryption using the `cryptography` library's hazmat (hazardous materials) primitives, which gives me low-level control while still using audited, secure implementations.

I chose AES-256 specifically because it uses 256-bit keys, which provides a very high security margin - it's the same standard used by governments for classified information. The 256-bit key comes from SHA-256 hashing the chess moves, which gives me exactly the right key length.

For the mode of operation, I chose CBC - Cipher Block Chaining - for several important reasons. First, CBC ensures that identical plaintext blocks encrypt to different ciphertext blocks because each block is XORed with the previous ciphertext block before encryption. This prevents patterns in the plaintext from showing up in the ciphertext, which is crucial for security.

In my implementation, I generate a random 16-byte initialization vector (IV) using `os.urandom(16)` for each encryption. This IV is prepended to the ciphertext, so it gets transmitted along with the encrypted data. This is standard practice - the IV doesn't need to be secret, just unpredictable. Having a random IV means encrypting the same message twice produces different ciphertexts.

I also implemented proper PKCS7 padding to handle messages that aren't exact multiples of the 16-byte AES block size. The padding adds bytes to make the plaintext length a multiple of 16, and includes information about how much padding was added so it can be correctly removed during decryption.

---

### 8. How does your LSB steganography implementation work at the bit level?

**Answer:** The LSB steganography implementation is really interesting when you break it down to the bit level. Let me walk through exactly what happens.

First, I convert the data I want to hide into a binary string. But before that, I add a 32-bit header that encodes the length of the data. This is crucial because when extracting, I need to know exactly how many bits to read. Without this header, I'd have no way to know where the hidden data ends.

For the actual embedding, I iterate through every pixel in the image. Each pixel has three color channels - red, green, and blue - and each channel is an 8-bit value from 0 to 255. I take the least significant bit of each channel value and replace it with one bit from my binary data.

Here's the clever part: I use a bitwise operation `(pixel_value & 254) | data_bit`. The `& 254` operation (254 is 11111110 in binary) masks off the LSB, setting it to zero while keeping all other bits unchanged. Then the `| data_bit` sets that LSB to whatever my data bit is. This means I'm only ever changing a pixel value by at most 1, which is imperceptible to human eyes.

For a typical image with, say, 400x400 pixels, that gives me 480,000 bits of capacity (400 × 400 × 3 channels), which is about 60 KB. That's plenty for encrypted messages and chess move lists.

During extraction, I do the reverse - I read through every pixel's RGB channels, extract the LSB using `pixel_value & 1`, build up the binary string, read the length from the first 32 bits, and then extract exactly that many data bits. The beauty is that this is completely lossless if the image isn't recompressed - I get back exactly what I put in.

---

### 9. What challenges did you face during development, and how did you solve them?

**Answer:** There were several interesting challenges that really pushed my problem-solving skills.

The biggest challenge was dealing with image file format limitations. LSB steganography only works with lossless image formats because lossy compression like JPEG can destroy the hidden data. I had to make sure my system always saved images as PNG and validated that input images were in appropriate formats. I added checks to convert images to RGB mode and preserve the pixel data exactly.

Another challenge was the chess move parsing. Chess moves can be notated in many ways - algebraic notation with move numbers like "1. e4 e5", or just the moves themselves, or even PGN format with headers and annotations. I had to write robust parsing functions to handle different input formats. My `parseMoveList` function uses regex to strip out move numbers and clean the input, and I validate everything through the `python-chess` library to ensure moves are legal.

A subtle but important issue was key derivation consistency. When generating the encryption key from chess moves, I needed to ensure that the same moves always produce the same key, regardless of formatting. I solved this by normalizing the move string before hashing - removing extra whitespace, using consistent capitalization, and validating through the chess library.

I also had to think carefully about error handling. What happens if someone provides an invalid FEN string, or tries to embed too much data for an image's capacity? I added validation checks that calculate the maximum capacity before attempting to embed, provide clear error messages, and fall back to safe defaults when possible - like using the starting position if an invalid FEN is provided.

The GUI integration was another challenge, especially synchronizing the Tkinter-based main interface with the Pygame-based chess game. I had to structure the code carefully to allow launching the chess game as a separate component that could return move data back to the main application.

---

### 10. How would you improve the security of this system against various attacks?

**Answer:** Great question - I've actually thought a lot about the attack surface and potential improvements.

First, let me address the current security model. Right now, the system is vulnerable to known-plaintext attacks if an attacker knows both the plaintext message and has the cipher image. They could potentially work backwards to derive the key. To mitigate this, I could implement a key-stretching function like PBKDF2 or Argon2 that takes the chess-derived key and applies thousands of iterations, making brute-force attacks computationally expensive.

Steganography detection is another concern. While LSB steganography is imperceptible to human eyes, statistical analysis tools can sometimes detect it by analyzing the distribution of LSBs, which should be random in natural images but become less random when data is embedded. I could improve this by implementing adaptive steganography that embeds data in more complex regions of images where the changes are harder to detect, or by using more sophisticated techniques like DCT (Discrete Cosine Transform) based steganography.

The chess key derivation could be strengthened by adding a user-specific salt or using a key derivation function that combines the chess moves with additional entropy. This would prevent attacks where someone builds a database of keys from famous chess games.

I'd also add authentication - currently, there's no way to verify that the message hasn't been tampered with. I could implement HMAC (Hash-based Message Authentication Code) to create a cryptographic signature that gets embedded alongside the encrypted data.

From a practical security standpoint, I'd add secure deletion of temporary files, memory wiping of sensitive variables, and possibly implement secure keyboard input for passphrases to prevent keyloggers.

Finally, the two-image approach, while providing some security, could be improved by implementing a proper secret-sharing scheme like Shamir's Secret Sharing, where you'd need a threshold number of images to reconstruct the message, providing even more resilience.

---

## Hard Level Questions (11-15)

### 11. Explain the mathematical foundation of how SHA-256 provides a suitable key for AES-256, and discuss the entropy considerations.

**Answer:** This gets into the cryptographic theory underlying the system, which I find fascinating.

SHA-256 is a cryptographic hash function that takes an input of arbitrary length and produces a 256-bit (32-byte) output. The critical properties that make it suitable for key derivation are preimage resistance, second-preimage resistance, and collision resistance. These properties ensure that you can't work backwards from the hash to find the input, you can't find a different input that produces the same hash, and it's computationally infeasible to find two inputs with the same hash.

For AES-256, we need a 256-bit key that's uniformly random and unpredictable. When I hash the chess moves with SHA-256, I'm essentially using it as a deterministic random bit generator. The avalanche effect of SHA-256 means that even a tiny change in the chess moves - like a single different move - produces a completely different hash output.

Now, the entropy question is crucial. The security of the system ultimately depends on the entropy of the chess moves, not the hash function itself. A typical chess game might have, say, 40 moves, where each move is chosen from an average of around 30-35 legal moves. This gives us roughly log₂(30)^80 ≈ 390 bits of entropy for a 40-move game (counting both white and black moves). That's more than the 256 bits we need for AES-256, so we're in good shape.

However, there's a practical concern: if someone uses a famous grandmaster game that's publicly available in databases, the effective entropy drops to nearly zero - an attacker could try all famous games. That's why in a real deployment, I'd recommend either using a game that's private to the sender and receiver, or adding additional entropy through a user passphrase or salt.

The SHA-256 compression of this entropy into a fixed 256-bit key is actually beneficial from an information-theoretic perspective. Even though the move sequence might be longer than 256 bits, we want a key of exactly 256 bits for AES-256. The hash function provides both the right length and proper distribution of bits.

---

### 12. Discuss the security trade-offs between your steganography approach and pure encryption. When would your system be preferred over traditional encrypted communication?

**Answer:** This is really about understanding when steganography adds value beyond just encryption, and when it might actually introduce vulnerabilities.

Pure encryption provides confidentiality through computational hardness - breaking AES-256 is infeasible with current technology. However, encrypted messages are obvious. If you send something that's clearly encrypted, you're advertising that you have a secret, which can itself be problematic. In some jurisdictions, encryption is restricted or suspicious. Law enforcement can demand you decrypt messages, and some countries have laws against certain types of encrypted communication.

Steganography adds security through obscurity - which is generally frowned upon as a sole security measure, but as a complementary layer, it provides real benefits. The goal is "security through undetectability." If an adversary doesn't know hidden data exists, they won't try to extract or decrypt it. This is particularly valuable in scenarios where having encrypted communication itself raises red flags.

However, there are trade-offs. Steganographic systems are vulnerable to steganalysis - statistical analysis that can detect hidden data. My LSB approach, while simple and effective for many use cases, is detectable by sophisticated analysis looking at LSB distributions, chi-square tests, or RS analysis. The embedded data makes the LSBs of pixel values less random than they would be naturally.

Additionally, any modification to the image destroys the hidden data. If someone screenshots the image, crops it, adjusts the colors, or saves it in a lossy format like JPEG, the steganographic payload is gone. Pure encryption doesn't have this fragility - the ciphertext remains intact through various transformations.

My system shines in scenarios where:

1. The communication channel is under surveillance, but the surveillance is looking for encrypted traffic
2. Plausible deniability is important - the images look like innocent chess diagrams
3. The key exchange problem is significant - sharing a chess game is more natural than sharing a random key
4. You're communicating with someone you have a shared context with (you both know or can play a chess game)

Where it's weaker:

1. Against sophisticated adversaries with steganalysis tools
2. When images might be recompressed or modified in transit
3. When you need to send large amounts of data efficiently
4. In scenarios where using encryption is legal and accepted

The ideal scenario is actually layered security: use strong encryption (which my system does with AES-256), then add steganography as an additional layer of obscurity, which makes it harder for adversaries to even know to attempt an attack.

---

### 13. If you were to scale this system for production use, what architectural changes would you make, and what additional features would you implement?

**Answer:** Moving from a proof-of-concept to a production system would require significant architectural changes across multiple dimensions.

First, the key management needs to be more robust. I'd implement a proper key derivation function like PBKDF2 or Argon2id that combines the chess moves with a user-specific salt and applies thousands of iterations. This prevents rainbow table attacks on common chess games. I'd also add support for key rotation and versioning, so you could use different chess games over time and the system tracks which key was used for each message.

For scalability, I'd move from a monolithic desktop application to a client-server architecture. The heavy cryptographic operations could be performed client-side for security, but you'd want server-side components for features like:

- Secure message queuing and storage
- User authentication and authorization
- Rate limiting and abuse prevention
- Audit logging for security compliance
- Multi-device synchronization

The steganography approach needs improvement for production. I'd implement multiple steganographic algorithms that users could choose based on their threat model: LSB for simplicity, DCT-based methods for JPEG compatibility, or more sophisticated adaptive techniques. I'd add automatic steganalysis to warn users if their image might be detectable.

For the chess component, I'd create a proper chess game database integration, allowing users to:

- Select from curated collections of games
- Import games from chess.com or lichess.org
- Generate random legal games programmatically
- Use a combination of multiple games for extra entropy

I'd add authentication and integrity verification through HMAC or digital signatures, so recipients can verify the message hasn't been tampered with and actually came from the claimed sender.

The image handling needs to be more sophisticated:

- Support for larger images with automatic capacity calculation
- Compression of data before embedding to maximize capacity
- Error correction codes to handle minor image modifications
- Support for multiple image types as cover images (not just chessboards)

For deployment, I'd containerize the application using Docker, implement comprehensive logging and monitoring, add automated testing with unit tests, integration tests, and security tests. I'd use tools like OWASP ZAP for security scanning and implement proper secret management using tools like HashiCorp Vault.

Performance optimizations would include:

- Parallel processing for large images using multiprocessing
- Caching of generated chessboard images
- Optimized NumPy operations for faster pixel manipulation
- Progressive image loading for better UX

Finally, I'd add enterprise features like:

- Multi-user support with role-based access control
- End-to-end encrypted messaging protocol
- Mobile applications with push notifications
- Integration APIs for third-party applications
- Compliance features for regulations like GDPR
- Comprehensive documentation and SDK for developers

---

### 14. Explain potential attack vectors against your system and how an attacker might attempt to decrypt messages without the key. How would you defend against these attacks?

**Answer:** Let me walk through the attack surface systematically, considering different adversary capabilities.

**Known-Plaintext Attack:** If an attacker has both a plaintext message and its corresponding encrypted image, they could potentially derive the key. In my current implementation, if they know the plaintext and ciphertext, they could theoretically brute-force the chess moves by trying combinations until the derived key successfully decrypts the message.

Defense: Implement key-stretching with thousands of iterations, making each guess computationally expensive. Add a per-user salt that's not stored in the images, requiring attackers to brute-force both the moves and the salt.

**Steganalysis:** Statistical analysis can detect LSB embedding. Chi-square tests, RS analysis, or machine learning models trained on pristine vs. stego images could flag my images as containing hidden data.

Defense: Implement adaptive steganography that only embeds in high-entropy regions of the image, use spread-spectrum techniques to distribute data across the image, or use frequency-domain methods like DCT that are harder to detect.

**Chess Game Database Attack:** An attacker could build a database of all famous chess games, derive keys from each, and try decrypting captured messages. Given that there are only a few million famous games, this is feasible.

Defense: Encourage users to use private games or combine multiple games. Add a passphrase component to the key derivation. Implement a key derivation function that makes each key derivation expensive (e.g., 100,000 iterations of PBKDF2).

**Man-in-the-Middle:** If an attacker can intercept and modify the images in transit, they could replace them with their own images.

Defense: Implement digital signatures using asymmetric cryptography. The sender signs the hash of both images, and the signature can be verified by the receiver. Add a cryptographic hash chain linking the two images so modifications are detectable.

**Side-Channel Attacks:** Timing attacks during encryption/decryption could leak information about the key. Memory dumps might expose plaintext or keys.

Defense: Use constant-time cryptographic operations, implement secure memory wiping of sensitive data after use, use mlock() to prevent paging sensitive data to disk.

**Compression-Based Attacks:** Since images with embedded data have different compression characteristics, attackers might detect hidden data by compressing images and analyzing the compression ratios.

Defense: Pre-compress data before embedding, use embedding techniques that maintain natural compression characteristics, implement cover-image selection that chooses images with naturally high entropy.

**Frequency Analysis on Chess Moves:** If the same chess games are reused, patterns in the encrypted messages might emerge.

Defense: Implement automatic key rotation, combine multiple games in unpredictable ways, add randomness to the key derivation process.

**Coercion Attacks:** Legal or physical coercion to reveal keys or decrypt messages.

Defense: Implement plausible deniability through hidden volumes (one chess game decrypts to a decoy message, another to the real message), add duress passwords that destroy keys or alert contacts.

**Implementation Vulnerabilities:** Bugs in my code could leak information - like not properly zeroing memory, using weak random number generation, or having buffer overflows.

Defense: Use well-audited cryptographic libraries (which I do), implement comprehensive input validation, add fuzzing tests, conduct security audits, use memory-safe languages or safe coding practices.

The key insight is that security is a holistic challenge. The cryptography might be mathematically sound, but practical attacks often exploit implementation details, user behavior, or side channels. A production system needs defense in depth across all these layers.

---

### 15. This is an impressive project that shows strong understanding of cryptography and steganography. Tell me about a specific bug or edge case you encountered that taught you something important about secure system design.

**Answer:** Great question - there was actually a really interesting bug I encountered that taught me a valuable lesson about the difference between theoretical security and practical security.

Early in development, I was testing the extraction and decryption process, and I kept getting incorrect plaintext output. The ciphertext would extract correctly, the key would derive correctly, but the decryption would produce garbage. After hours of debugging, I traced it to a subtle issue with how I was handling the initialization vector.

Here's what happened: In AES-CBC mode, I generate a random 16-byte IV and prepend it to the ciphertext before embedding. During decryption, I extract the ciphertext and separate the IV from the actual encrypted data. The bug was in my padding removal function. When I removed PKCS7 padding, I was reading the last byte to determine how many padding bytes to remove. But occasionally, the last byte of legitimate plaintext happened to be a value that looked like valid padding - say, the plaintext ended with the character '\x03', which looks like "3 bytes of padding."

This caused my padding removal to incorrectly strip actual message content, corrupting the plaintext. The lesson here was profound: you can't just look at the last byte in isolation. PKCS7 padding is valid only if the last N bytes are all the same value N. So if the last byte is 3, the previous two bytes must also be 3 for it to be valid padding.

I fixed this by implementing proper PKCS7 validation - checking that the padding value is reasonable (1-16 for AES), and that all the padding bytes have the correct value. If the validation fails, it indicates either data corruption or a decryption error, probably due to the wrong key.

This bug taught me several important lessons about secure system design:

First, **validate everything, especially at security boundaries**. The decryption boundary is critical - if your decryption appears to succeed but produces garbage, you might leak information about whether a key is correct through timing or error messages.

Second, **edge cases in cryptographic implementations can create vulnerabilities**. What seemed like a simple "read the last byte" operation actually needed careful validation. This is why using well-audited libraries is so important - they've thought through all these edge cases.

Third, **testing with diverse inputs is crucial**. My initial tests used simple ASCII messages that didn't trigger this bug. Only when I tested with longer messages and various Unicode characters did the issue surface. In production cryptographic systems, you need to test with random binary data, edge-case lengths, and adversarial inputs.

Fourth, **error handling in cryptographic systems is sensitive**. I had to be careful about what error messages I returned. Saying "invalid padding" tells an attacker they successfully decrypted to the padding stage, which leaks information. Better to return a generic "decryption failed" message.

This experience really drove home that cryptography is unforgiving of small mistakes. A single byte handled incorrectly can compromise the entire system. It's reinforced my appreciation for using established libraries and thoroughly testing security-critical code. It's also made me much more careful about assuming things work correctly - I now validate assumptions at every step, especially around cryptographic operations.

The debugging process itself was educational too - I learned to use proper debugging techniques for crypto code, like hexdumping data at each stage, verifying hash values match expected outputs, and building unit tests for each cryptographic primitive in isolation before integrating them.

---

## Additional Tips for the Career Fair

When discussing this project:

- **Be enthusiastic** - Show genuine interest in the cryptographic concepts
- **Connect to the company** - If interviewing at a security company, emphasize security aspects. For a general tech company, emphasize software engineering practices
- **Be honest about limitations** - If asked about something you don't know, acknowledge it and explain how you'd research it
- **Relate to real-world applications** - Mention use cases like secure journalism, private communication, or digital rights
- **Highlight soft skills** - Problem-solving, persistence through debugging, self-directed learning
- **Show continuous improvement** - Mention what you'd do differently or improve next time
- **Be ready for follow-ups** - Each answer might spark deeper technical questions

Good luck at the career fair!
