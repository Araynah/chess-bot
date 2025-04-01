import chess
import random


class OpeningBook:

    def __init__(self, book_path=None):

        self.book = {}  # Dictionary: FEN -> list of (move, weight) tuples

        if book_path:

            self.load_book(book_path)

           

    def load_book(self, book_path):

        """Load opening book from file"""

        # Polyglot book loading implementation

        try:

            with open(book_path, "rb") as book_file:

                while True:

                    entry_data = book_file.read(16)

                    if len(entry_data) < 16:

                        break

                   

                    key = int.from_bytes(entry_data[0:8], byteorder="big")

                    move = int.from_bytes(entry_data[8:10], byteorder="big")

                    weight = int.from_bytes(entry_data[10:12], byteorder="big")

                    learn = int.from_bytes(entry_data[12:16], byteorder="big")

                   

                    # Convert key to FEN, move to UCI notation

                    fen = self._key_to_fen(key)  # Simplified, actual implementation is complex

                    uci_move = self._bin_to_uci(move)

                   

                    if fen in self.book:

                        self.book[fen].append((uci_move, weight))

                    else:

                        self.book[fen] = [(uci_move, weight)]

        except Exception as e:

            print(f"Error loading opening book: {e}")

           

    def get_move(self, board, variation=0.1):

        """Get a move from the opening book for the current position"""

        try:

            # Get simplified FEN (only piece positions and turn)

            fen = self._simplified_fen(board)

           

            if fen in self.book:

                moves = self.book[fen]

               

                # Sort by weight, highest first

                moves.sort(key=lambda x: x[1], reverse=True)

               

                # Introduce variation if requested

                if variation > 0 and len(moves) > 1:

                    # Sometimes pick not the best move but a random good one

                    if random.random() < variation:

                        # Pick from top 3 moves with probability proportional to weight

                        top_moves = moves[:min(3, len(moves))]

                        total_weight = sum(weight for _, weight in top_moves)


                        r = random.random() * total_weight

                        cumulative = 0

                        for move, weight in top_moves:

                            cumulative += weight

                            if r <= cumulative:

                                return move

               

                # Default: return highest weighted move

                return moves[0][0]

           

            return None  # No book move available

        except Exception as e:

            print(f"Error getting book move: {e}")

            return None

           

    def _simplified_fen(self, board):

        """Return simplified FEN (position and turn only)"""

        full_fen = board.fen()

        return ' '.join(full_fen.split(' ')[:2])
    

def create_simple_book():
    """
    Create a simple in-memory opening book.
    
    Returns:
        dict: A dictionary mapping simplified FEN positions (up to side to move)
              to a list of tuples (uci_move, weight).
    """

    book = {}  # Dictionary to store the opening book: FEN -> list of (move, weight)

    def add_line(moves, base_weight=100, decay=10):
        """
        Add a sequence of SAN moves to the book, assigning decreasing weights.

        Args:
            moves (list): A list of moves in SAN format (e.g., ['e4', 'e5', 'Nf3']).
            base_weight (int): Starting weight for the first move in the line.
            decay (int): How much to decrease the weight per move.
        """
        board = chess.Board()

        for i, move in enumerate(moves):
            # Generate simplified FEN (only position and side to move)
            fen = board.fen().split(' ')[0] + ' ' + ('w' if board.turn else 'b')

            # Convert SAN move to UCI format
            uci = chess.Move.from_san(move).uci()

            # Apply decreasing weight for moves deeper in the line
            weight = base_weight - i * decay

            # Add move to the book under the FEN position
            if fen in book:
                book[fen].append((uci, weight))
            else:
                book[fen] = [(uci, weight)]

            # Play the move on the board to get the next position
            board.push_san(move)

    # 🧠 Basic opening moves
    add_line(["e4"])        # King's Pawn
    add_line(["d4"])        # Queen's Pawn
    add_line(["c4"])        # English
    add_line(["Nf3"])       # Réti

    # 🧠 Common black responses
    add_line(["e4", "e5"])  # Open Game
    add_line(["e4", "c5"])  # Sicilian Defense
    add_line(["e4", "e6"])  # French Defense
    add_line(["e4", "c6"])  # Caro-Kann

    add_line(["d4", "d5"])  # Closed Game
    add_line(["d4", "Nf6"]) # Indian Defense
    add_line(["d4", "f5"])  # Dutch Defense
    add_line(["d4", "e6"])  # Queen's Pawn Game

    # 🧠 Popular opening lines
    add_line(["e4", "e5", "Nf3", "Nc6", "Bb5"])  # Ruy López
    add_line(["e4", "e5", "Nf3", "Nc6", "Bc4"])  # Italian Game
    add_line(["d4", "d5", "c4"])                # Queen's Gambit
    add_line(["Nf3", "d5", "c4"])               # Réti Gambit setup
    add_line(["c4", "e5"])                      # Reversed Sicilian

    return book

# At the bottom of book.py

def update_opening_weights(book, game, game_result, player_color):
    """
    Update opening book weights based on game results.

    Args:
        book (dict): The opening book dictionary (FEN → [(uci_move, weight)]).
        game_result (str): '1-0', '0-1', or '1/2-1/2'.
        player_color (bool): True if player was White, False if Black.
    """
    import chess.pgn 

    board = chess.Board()
    moves_played = []

    for move in game.mainline_moves():
        fen = board.fen().split(' ')[0] + (' w' if board.turn else ' b')

        if fen in book:
            uci = move.uci()
            for i, (book_move, weight) in enumerate(book[fen]):
                if book_move == uci:
                    moves_played.append((fen, i))
                    break

        board.push(move)

        if len(moves_played) == 0:
            break  # Player left the book early

    # Determine how to modify weights based on result
    result_modifier = 0
    if game_result == '1-0':
        result_modifier = 1 if player_color else -1
    elif game_result == '0-1':
        result_modifier = -1 if player_color else 1

    # Update the weights
    for fen, move_index in moves_played:
        move_uci, weight = book[fen][move_index]
        new_weight = max(1, weight + result_modifier * 5)
        book[fen][move_index] = (move_uci, new_weight)
