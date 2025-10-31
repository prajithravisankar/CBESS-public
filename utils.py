# =================================================IMPORT STATEMENTS====================================================
import chess
import chess.pgn
from PIL import Image, ImageDraw
import os
from io import StringIO

from chess import PIECE_SYMBOLS

# ======================================================================================================================

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
base_path = os.path.join(script_dir, 'chessPieces')

# Use relative paths to the chess piece images
chessPieceImages = {
    # Black pieces
    'r': os.path.join(base_path, 'r.png'),
    'n': os.path.join(base_path, 'n.png'),
    'b': os.path.join(base_path, 'b.png'),
    'q': os.path.join(base_path, 'q.png'),
    'k': os.path.join(base_path, 'k.png'),
    'p': os.path.join(base_path, 'p.png'),

    # White pieces
    'R': os.path.join(base_path, 'RW.png'),
    'N': os.path.join(base_path, 'NW.png'),
    'B': os.path.join(base_path, 'BW.png'),
    'Q': os.path.join(base_path, 'QW.png'),
    'K': os.path.join(base_path, 'KW.png'),
    'P': os.path.join(base_path, 'PW.png')
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