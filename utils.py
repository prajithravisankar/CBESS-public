# =================================================IMPORT STATEMENTS====================================================
import chess
import chess.pgn
from PIL import Image, ImageDraw
import os
from io import StringIO

from chess import PIECE_SYMBOLS

# ======================================================================================================================

# change to relative paths if someone else is trying to run this program
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
                imgPath =chessPieceImages[symbol]
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


def getGamePositions(moves: str):
    """
    takes a string of chess moves (in algebraic notation) and returns a list of FEN strings representing the
    board position after each move.
    :param moves: string of moves to be parsed
    :return: list of FEN positions
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