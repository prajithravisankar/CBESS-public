import pygame
import chess
import chess.engine
import sys
import os
import pyperclip
from pygame.locals import *


class ChessGame:
    def __init__(self):
        '''
        creates chess game window with board, pieces, and game controls using pygame
        '''
        # Initialize pygame
        pygame.init()

        # Set up the display
        self.WIDTH, self.HEIGHT = 900, 650
        self.BOARD_SIZE = 560
        self.SQUARE_SIZE = self.BOARD_SIZE // 8
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Chess vs Stockfish")

        # Load chess pieces
        self.pieces = {}
        piece_files = {
            'p': 'p.png', 'r': 'r.png', 'n': 'n.png', 'b': 'b.png', 'q': 'q.png', 'k': 'k.png',
            'P': 'PW.png', 'R': 'RW.png', 'N': 'NW.png', 'B': 'BW.png', 'Q': 'QW.png', 'K': 'KW.png'
        }

        # Custom piece paths
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.join(script_dir, 'chessPieces')  # Assuming 'chessPieces' directory

        # Try to load custom pieces, fallback to pygame drawing if fails
        try:
            for piece, file in piece_files.items():
                path = os.path.join(self.base_path, file)
                if os.path.exists(path):
                    img = pygame.image.load(path)
                    self.pieces[piece] = pygame.transform.scale(img, (self.SQUARE_SIZE - 10, self.SQUARE_SIZE - 10))
                else:
                    self.pieces = {}  # If any file is missing, use fallback drawing
                    print(f"Could not find piece image: {path}")
                    break
        except Exception as e:
            self.pieces = {}
            print(f"Error loading pieces: {e}")

        # Initialize the board
        self.board = chess.Board()

        # Initialize Stockfish engine
        self.engine = None  # Initialize engine to None
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci("stockfish")
            self.engine.configure({"Skill Level": 10})  # Adjust skill level as needed
        except Exception as e:
            print(f"Error starting Stockfish: {e}")
            print("Make sure Stockfish is installed and in your PATH.")
            # Don't exit - allow human vs human play even if engine fails

        # Game state variables
        self.selected_square = None
        self.move_list = []
        self.player_color = chess.WHITE
        self.game_over = False
        self.valid_moves = []
        self.copy_success = False
        self.copy_success_time = 0
        self.vs_ai = True  # Default to AI mode

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.LIGHT_SQUARE = (240, 217, 181)
        self.DARK_SQUARE = (181, 136, 99)
        self.HIGHLIGHT = (124, 252, 0, 128)  # Semi-transparent green
        self.VALID_MOVE_COLOR = (100, 149, 237, 150)  # Semi-transparent cornflower blue
        self.TEXT_COLOR = (50, 50, 50)
        self.PANEL_BG = (245, 245, 245)
        self.MOVE_WHITE_BG = (240, 240, 240)
        self.MOVE_BLACK_BG = (220, 220, 220)
        self.BUTTON_COLOR = (70, 130, 180)  # Steel blue
        self.BUTTON_HOVER_COLOR = (100, 149, 237)  # Cornflower blue
        self.BUTTON_TEXT_COLOR = (255, 255, 255)
        self.BUTTON_AI_COLOR = (144, 238, 144)  # LightGreen
        self.BUTTON_HUMAN_COLOR = (255, 182, 193)  # LightPink

        # Font
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.move_font = pygame.font.SysFont('Arial', 18)
        self.button_font = pygame.font.SysFont('Arial', 18, bold=True)

        # Move list scroll position
        self.move_scroll = 0
        self.max_visible_moves = 15

        # Button state
        self.copy_button_rect = None
        self.copy_button_hover = False

        # Scroll button rectangles
        self.scroll_up_rect = None
        self.scroll_down_rect = None

        # AI vs Human buttons
        self.ai_button_rect = None
        self.human_button_rect = None

        # Clock
        self.clock = pygame.time.Clock()

    def draw_board(self):
        """
        renders chess board and its elements in pygame window
        :return:
        """
        board_offset_x = 20
        board_offset_y = (self.HEIGHT - self.BOARD_SIZE) // 2

        # Draw the chess board
        for row in range(8):
            for col in range(8):
                x = board_offset_x + col * self.SQUARE_SIZE
                y = board_offset_y + row * self.SQUARE_SIZE
                color = self.LIGHT_SQUARE if (row + col) % 2 == 0 else self.DARK_SQUARE
                pygame.draw.rect(self.screen, color, (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))

                # Draw coordinates
                if col == 0:  # Ranks (numbers)
                    text = self.font.render(str(8 - row), True,
                                            self.BLACK if color == self.LIGHT_SQUARE else self.WHITE)
                    self.screen.blit(text, (x + 5, y + 5))
                if row == 7:  # Files (letters)
                    text = self.font.render(chr(97 + col), True,
                                            self.BLACK if color == self.LIGHT_SQUARE else self.WHITE)
                    self.screen.blit(text, (x + self.SQUARE_SIZE - 15, y + self.SQUARE_SIZE - 20))

        # Draw board border
        pygame.draw.rect(self.screen, self.BLACK,
                         (board_offset_x - 2, board_offset_y - 2,
                          self.BOARD_SIZE + 4, self.BOARD_SIZE + 4), 2)

        # Highlight selected square if any
        if self.selected_square is not None:
            col, row = self.selected_square % 8, self.selected_square // 8
            x = board_offset_x + col * self.SQUARE_SIZE
            y = board_offset_y + (7 - row) * self.SQUARE_SIZE  # Flip row for display
            highlight = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
            highlight.fill(self.HIGHLIGHT)
            self.screen.blit(highlight, (x, y))

            # Calculate and highlight valid moves
            self.valid_moves = [move for move in self.board.legal_moves if move.from_square == self.selected_square]
            for move in self.valid_moves:
                to_col, to_row = move.to_square % 8, move.to_square // 8
                to_x = board_offset_x + to_col * self.SQUARE_SIZE
                to_y = board_offset_y + (7 - to_row) * self.SQUARE_SIZE  # Flip row for display

                # If there's an enemy piece at the destination, highlight the whole square
                to_piece = self.board.piece_at(move.to_square)
                if to_piece and to_piece.color != self.player_color:
                    # Draw a semi-transparent red square
                    capture = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
                    capture.fill((255, 0, 0, 100))  # Semi-transparent red
                    self.screen.blit(capture, (to_x, to_y))
                else:
                    # Draw a circle for empty square moves
                    pygame.draw.circle(self.screen, self.VALID_MOVE_COLOR,
                                       (to_x + self.SQUARE_SIZE // 2, to_y + self.SQUARE_SIZE // 2),
                                       self.SQUARE_SIZE // 6)

        return board_offset_x, board_offset_y

    def draw_pieces(self, board_offset_x, board_offset_y):
        """
        renders chess pieces in the board
        :param board_offset_x: top left x coordinate
        :param board_offset_y: top left y coordinate
        :return: none
        """
        # Draw the chess pieces on the board
        for row in range(8):
            for col in range(8):
                square = chess.square(col, 7 - row)  # Convert to chess.py coordinates
                piece = self.board.piece_at(square)

                if piece:
                    x = board_offset_x + col * self.SQUARE_SIZE + 5  # Center the piece
                    y = board_offset_y + row * self.SQUARE_SIZE + 5
                    piece_symbol = piece.symbol()

                    # Check if we have the image for this piece, if we do draw that piece
                    if piece_symbol in self.pieces:
                        self.screen.blit(self.pieces[piece_symbol], (x, y))
                    else:
                        # Fallback: draw colored circles with letters
                        color = self.WHITE if piece.color == chess.WHITE else self.BLACK
                        pygame.draw.circle(self.screen, color,
                                           (x + self.SQUARE_SIZE // 2 - 5, y + self.SQUARE_SIZE // 2 - 5),
                                           self.SQUARE_SIZE // 2 - 5)
                        text = self.font.render(piece_symbol, True,
                                                self.BLACK if piece.color == chess.WHITE else self.WHITE)
                        text_rect = text.get_rect(center=(x + self.SQUARE_SIZE // 2 - 5, y + self.SQUARE_SIZE // 2 - 5))
                        self.screen.blit(text, text_rect)

    def draw_buttons(self):
        """Draw buttons for AI vs Human and copy moves at the bottom of the screen."""

        # Button dimensions and positioning
        button_width = (self.WIDTH - 40) // 3  # Three buttons with space between
        button_height = 40
        button_y = self.HEIGHT - 50

        # AI Button
        ai_button_x = 10
        self.ai_button_rect = pygame.Rect(ai_button_x, button_y, button_width, button_height)

        ai_button_color = self.BUTTON_AI_COLOR if self.vs_ai else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, ai_button_color, self.ai_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, self.BLACK, self.ai_button_rect, 1, border_radius=5)

        ai_text = self.button_font.render("AI Mode", True, self.BUTTON_TEXT_COLOR)
        ai_text_rect = ai_text.get_rect(center=self.ai_button_rect.center)
        self.screen.blit(ai_text, ai_text_rect)

        # Human Button
        human_button_x = ai_button_x + button_width + 10
        self.human_button_rect = pygame.Rect(human_button_x, button_y, button_width, button_height)

        human_button_color = self.BUTTON_HUMAN_COLOR if not self.vs_ai else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, human_button_color, self.human_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, self.BLACK, self.human_button_rect, 1, border_radius=5)

        human_text = self.button_font.render("Human Mode", True, self.BUTTON_TEXT_COLOR)
        human_text_rect = human_text.get_rect(center=self.human_button_rect.center)
        self.screen.blit(human_text, human_text_rect)

        # Copy Moves Button
        copy_button_x = human_button_x + button_width + 10
        self.copy_button_rect = pygame.Rect(copy_button_x, button_y, button_width, button_height)

        button_color = self.BUTTON_HOVER_COLOR if self.copy_button_hover else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, self.copy_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, self.BLACK, self.copy_button_rect, 1, border_radius=5)

        copy_text = self.button_font.render("Copy Moves", True, self.BUTTON_TEXT_COLOR)
        copy_text_rect = copy_text.get_rect(center=self.copy_button_rect.center)
        self.screen.blit(copy_text, copy_text_rect)

    def draw_move_list(self):
        # Calculate positions
        panel_width = 280
        panel_x = self.WIDTH - panel_width - 10
        panel_y = 20
        panel_height = self.HEIGHT - 40

        # Draw the move list panel
        pygame.draw.rect(self.screen, self.PANEL_BG, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, self.BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

        # Title
        title = self.title_font.render("Move History", True, self.BLACK)
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, panel_y + 20))
        self.screen.blit(title, title_rect)

        # Status
        status_text = ""
        if self.board.is_checkmate():
            status_text = "Checkmate!"
        elif self.board.is_stalemate():
            status_text = "Stalemate!"
        elif self.board.is_check():
            status_text = "Check!"

        if status_text:
            status = self.title_font.render(status_text, True, (180, 0, 0))
            status_rect = status.get_rect(center=(panel_x + panel_width // 2, panel_y + 50))
            self.screen.blit(status, status_rect)

        # Draw scroll buttons
        if len(self.move_list) > self.max_visible_moves * 2:
            # Up button
            up_rect = pygame.Rect(panel_x + panel_width - 30, panel_y + 70, 20, 20)
            pygame.draw.rect(self.screen, (200, 200, 200), up_rect)
            pygame.draw.rect(self.screen, self.BLACK, up_rect, 1)
            up_arrow = self.font.render("▲", True, self.BLACK)
            self.screen.blit(up_arrow, (up_rect.centerx - 5, up_rect.centery - 7))
            self.scroll_up_rect = up_rect

            # Down button
            down_rect = pygame.Rect(panel_x + panel_width - 30, panel_y + panel_height - 90, 20, 20)
            pygame.draw.rect(self.screen, (200, 200, 200), down_rect)
            pygame.draw.rect(self.screen, self.BLACK, down_rect, 1)
            down_arrow = self.font.render("▼", True, self.BLACK)
            self.screen.blit(down_arrow, (down_rect.centerx - 5, down_rect.centery - 7))
            self.scroll_down_rect = down_rect
        else:
            self.scroll_up_rect = None
            self.scroll_down_rect = None

        # Draw move list headers
        header_y = panel_y + 70
        pygame.draw.rect(self.screen, (220, 220, 220), (panel_x + 10, header_y, panel_width - 20, 25))
        pygame.draw.line(self.screen, self.BLACK, (panel_x + 10, header_y + 25),
                         (panel_x + panel_width - 10, header_y + 25))

        move_num_header = self.move_font.render("#", True, self.BLACK)
        white_header = self.move_font.render("White", True, self.BLACK)
        black_header = self.move_font.render("Black", True, self.BLACK)

        self.screen.blit(move_num_header, (panel_x + 20, header_y + 5))
        self.screen.blit(white_header, (panel_x + 60, header_y + 5))
        self.screen.blit(black_header, (panel_x + 170, header_y + 5))

        # Draw move list
        moves_start_y = header_y + 30

        for i in range(self.move_scroll,
                       min(self.move_scroll + self.max_visible_moves, (len(self.move_list) + 1) // 2)):
            move_row = i * 2
            row_y = moves_start_y + (i - self.move_scroll) * 30

            # Move number
            move_num = self.move_font.render(f"{i + 1}.", True, self.BLACK)
            self.screen.blit(move_num, (panel_x + 20, row_y + 5))

            # White's move
            if move_row < len(self.move_list):
                white_bg = pygame.Rect(panel_x + 50, row_y, 100, 25)
                pygame.draw.rect(self.screen, self.MOVE_WHITE_BG, white_bg)
                pygame.draw.rect(self.screen, self.BLACK, white_bg, 1)

                white_move = self.move_font.render(self.move_list[move_row], True, self.BLACK)
                white_rect = white_move.get_rect(center=(white_bg.centerx, white_bg.centery))
                self.screen.blit(white_move, white_rect)

            # Black's move
            if move_row + 1 < len(self.move_list):
                black_bg = pygame.Rect(panel_x + 160, row_y, 100, 25)
                pygame.draw.rect(self.screen, self.MOVE_BLACK_BG, black_bg)
                pygame.draw.rect(self.screen, self.BLACK, black_bg, 1)

                black_move = self.move_font.render(self.move_list[move_row + 1], True, self.BLACK)
                black_rect = black_move.get_rect(center=(black_bg.centerx, black_bg.centery))
                self.screen.blit(black_move, black_rect)

        # Total moves counter
        moves_text = f"Total Moves: {len(self.move_list)}"
        moves_surface = self.font.render(moves_text, True, self.BLACK)
        moves_rect = moves_surface.get_rect(center=(panel_x + panel_width // 2, panel_y + panel_height - 20))
        self.screen.blit(moves_surface, moves_rect)

        # Current turn indicator
        turn_text = "White's turn" if self.board.turn == chess.WHITE else "Black's turn"
        turn_surface = self.font.render(turn_text, True, self.BLACK)
        turn_rect = turn_surface.get_rect(center=(panel_x + panel_width // 2, panel_y + panel_height - 40))
        self.screen.blit(turn_surface, turn_rect)

        return panel_x, panel_width

    def format_moves_for_clipboard(self):
        """Format the moves in standard chess notation for clipboard"""
        if not self.move_list:
            return "No moves played yet"

        formatted_text = ""
        for i in range(0, len(self.move_list), 2):
            move_num = i // 2 + 1
            white_move = self.move_list[i]

            if i + 1 < len(self.move_list):
                black_move = self.move_list[i + 1]
                formatted_text += f"{move_num}. {white_move} {black_move} "
            else:
                formatted_text += f"{move_num}. {white_move} "

        return formatted_text.strip()

    def copy_moves_to_clipboard(self):
        """Copy the game moves to clipboard"""
        formatted_moves = self.format_moves_for_clipboard()
        try:
            pyperclip.copy(formatted_moves)
            self.copy_success = True
            self.copy_success_time = pygame.time.get_ticks()
        except Exception as e:
            print(f"Failed to copy to clipboard: {e}")

    def make_player_move(self, from_square, to_square):
        move = chess.Move(from_square, to_square)

        # Check for promotion
        if (self.board.piece_at(from_square) and
                self.board.piece_at(from_square).piece_type == chess.PAWN and
                ((to_square < 8 and self.player_color == chess.WHITE) or
                 (to_square >= 56 and self.player_color == chess.BLACK))):
            # Always promote to queen for simplicity (could add a dialog for options)
            move = chess.Move(from_square, to_square, promotion=chess.QUEEN)

        if move in self.valid_moves:
            san = self.board.san(move)
            self.board.push(move)
            self.move_list.append(san)

            # Auto-scroll to the bottom of move list
            total_move_rows = (len(self.move_list) + 1) // 2
            self.move_scroll = max(0, total_move_rows - self.max_visible_moves)
            return True
        return False

    def make_engine_move(self):
        if self.engine is not None:
            result = self.engine.play(self.board, chess.engine.Limit(time=1.0))
            san = self.board.san(result.move)
            self.board.push(result.move)
            self.move_list.append(san)

            # Auto-scroll to the bottom of move list
            total_move_rows = (len(self.move_list) + 1) // 2
            self.move_scroll = max(0, total_move_rows - self.max_visible_moves)

    def handle_click(self, pos, board_offset_x, board_offset_y, panel_x, panel_width):
        total_move_rows = (len(self.move_list) + 1) // 2
        max_scroll = max(0, total_move_rows - self.max_visible_moves)

        # Check if click is on the AI/Human buttons
        if self.ai_button_rect and self.ai_button_rect.collidepoint(pos):
            self.vs_ai = True
            self.board.reset()  # Reset the board on mode change
            self.move_list = []
            self.move_scroll = 0
            self.selected_square = None

            self.player_color = chess.WHITE
            if self.engine is None:
                print("Stockfish engine not available")
            return  # Important, exit as nothing else is to be done

        if self.human_button_rect and self.human_button_rect.collidepoint(pos):
            self.vs_ai = False
            self.board.reset()  # Reset the board on mode change
            self.move_list = []
            self.move_scroll = 0
            self.selected_square = None

            self.player_color = chess.WHITE
            return  # Important, exit as nothing else is to be done

        # Check if click is on the copy button
        if self.copy_button_rect and self.copy_button_rect.collidepoint(pos):
            self.copy_moves_to_clipboard()
            return

        # Check if click is on the move list scroll buttons
        if self.scroll_up_rect and self.scroll_up_rect.collidepoint(pos):
            if self.move_scroll > 0:
                self.move_scroll -= 1
            return

        if self.scroll_down_rect and self.scroll_down_rect.collidepoint(pos):
            if self.move_scroll < max_scroll:
                self.move_scroll += 1
            return

        # Check if click is on the board
        if (board_offset_x <= pos[0] <= board_offset_x + self.BOARD_SIZE and
                board_offset_y <= pos[1] <= board_offset_y + self.BOARD_SIZE):

            # Convert click position to board square
            col = (pos[0] - board_offset_x) // self.SQUARE_SIZE
            row = 7 - (pos[1] - board_offset_y) // self.SQUARE_SIZE  # Flip row for chess coordinates
            square = chess.square(col, row)

            # If a square is already selected, try to move
            if self.selected_square is not None:
                # Check if the clicked square is a valid destination
                move = chess.Move(self.selected_square, square)
                # Check for promotion
                if (self.board.piece_at(self.selected_square) and
                        self.board.piece_at(self.selected_square).piece_type == chess.PAWN and
                        ((square < 8 and self.player_color == chess.WHITE) or
                         (square >= 56 and self.player_color == chess.BLACK))):
                    move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)

                if move in self.valid_moves:
                    if self.make_player_move(self.selected_square, square):
                        self.selected_square = None
                        self.valid_moves = []

                        # If the game is not over, and we are playing against AI, make the engine's move
                        if not self.is_game_over() and self.vs_ai:
                            # Add a small delay before engine move for better user experience
                            pygame.time.delay(300)
                            self.make_engine_move()

                            # Check if the game is over after the engine's move
                            self.is_game_over()
                        else:
                            # Switch player turn if it's human vs human
                            self.player_color = not self.player_color

                    return

                # If not a valid move, select the new square if it has a piece of the player's color
                piece = self.board.piece_at(square)
                if piece and piece.color == self.board.turn and (self.vs_ai or self.board.turn == self.player_color):
                    self.selected_square = square
                    return
                else:
                    self.selected_square = None
                    self.valid_moves = []
                    return

            # No square selected yet, select if it has a piece of the player's color
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn and (self.vs_ai or self.board.turn == self.player_color):
                self.selected_square = square

    def is_game_over(self):
        if self.board.is_game_over():
            self.game_over = True
            return True
        return False

    def update_button_hover(self, mouse_pos):
        if self.copy_button_rect:
            self.copy_button_hover = self.copy_button_rect.collidepoint(mouse_pos)

    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            self.update_button_hover(mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    self.handle_click(event.pos, *self.board_panel_info, *self.move_panel_info)

                # Add mouse wheel scrolling
                elif event.type == pygame.MOUSEWHEEL:
                    total_move_rows = (len(self.move_list) + 1) // 2
                    max_scroll = max(0, total_move_rows - self.max_visible_moves)

                    if event.y > 0 and self.move_scroll > 0:  # Scroll up
                        self.move_scroll = max(0, self.move_scroll - 1)
                    elif event.y < 0 and self.move_scroll < max_scroll:  # Scroll down
                        self.move_scroll = min(max_scroll, self.move_scroll + 1)

            # Clear the screen
            self.screen.fill((230, 230, 230))  # Light gray background

            # Draw the board and pieces
            self.board_panel_info = self.draw_board()
            self.draw_pieces(*self.board_panel_info)

            # Draw the move list
            self.move_panel_info = self.draw_move_list()

            # Draw buttons
            self.draw_buttons()

            # Update the display
            pygame.display.flip()

            # If its AI's turn, make the AI move
            if self.vs_ai and not self.game_over and self.board.turn != self.player_color:
                pygame.time.delay(300)
                self.make_engine_move()

            # Cap the frame rate
            self.clock.tick(60)

        # Quit the game and close the engine
        if self.engine:
            self.engine.quit()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = ChessGame()
    game.run()