import chess
from book import OpeningBook


from board import ChessBoard

class ChessBot:
    
    def __init__(self,book_path=None):
        """
        Initialize the ChessBot with an optional opening book.
        
        Args:
            book_path (str, optional): Path to the opening book file.
        """

        self.book = OpeningBook(book_path)

        self.transposition_table = {}

        self.history_table = {}

    def choose_move(self, board, depth=4):
        """
        Select the best move for the current board state.
        
        First, check if an opening book move is available; if not, use the search algorithm.
        
        Args:
            board: A ChessBoard object.
            depth (int): Search depth for the minimax algorithm.
        
        Returns:
            chess.Move: The selected move.
        """

        # First check if we have a book move

        book_move = self.book.get_move(board)

        if book_move:

            # Verify the move is legal

            try:

                move = chess.Move.from_uci(book_move)

                if move in board.legal_moves:

                    return move

            except ValueError:

                pass  # Invalid UCI format, ignore

       

        # No book move, use search algorithm

        return self.minimax(board, depth)

    def evaluate_position(self, board):

        """
        Evaluate the current board position.
        
        Positive values favor white; negative values favor black.
        Evaluation considers material, pawn structure, king safety, and mobility.
        
        Args:
            board: A ChessBoard object.
        
        Returns:
            int: The evaluation score.
        """

        board_state = board.get_board_state()
        is_over = board.is_game_over()

        if is_over:

            if board_state.is_checkmate():

                return -10000 if board_state.turn else 10000

            return 0  # Draw


        score = 0
 

        # Material and piece position evaluation
        score += self.evaluate_material(board)

        # Pawn structure
        score += self.evaluate_pawn_structure(board)

        # King safety
        score += self.evaluate_king_safety(board)

        # Mobility
        score += self.evaluate_mobility(board)

        return score

    def evaluate_material(self, board):
        """
        Evaluate board material using standard piece values and a bishop pair bonus.
        
        Args:
            board: A ChessBoard object.
        
        Returns:
            int: Material evaluation score.
        """

        board_state = board.get_board_state()

        score = 0

        piece_values = {

            chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
            chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000

            }

        # Count material for white and black

        for piece in piece_values:

            score += len(board_state.pieces(piece, True)) * piece_values[piece]

            score -= len(board_state.pieces(piece, False)) * piece_values[piece]

        

        # Add bishop pair bonus for each side

        if len(board_state.pieces(chess.BISHOP, True)) >= 2:

            score += 50

        if len(board_state.pieces(chess.BISHOP, False)) >= 2:

            score -= 50


        return score
    

    def evaluate_mobility(self, board):
        """
        Evaluate the mobility of pieces by counting potential attacks.
        
        Args:
            board: A ChessBoard object.
        
        Returns:
            float: Mobility score.
        """
        
        board_state = board.get_board_state()

        score = 0
        piece_mobility_weights = {
            chess.PAWN: 0.1,    
            chess.KNIGHT: 0.3,  
            chess.BISHOP: 0.3,  
            chess.ROOK: 0.5,    
            chess.QUEEN: 0.9,  
            chess.KING: 0.2   
        }

        # Evaluate mobility for both white and black
        for color in [True, False]:
            multiplier = 1 if color else -1  # Positive for White, negative for Black
            mobility_score = 0

            for piece in piece_mobility_weights:
                piece_moves = sum(
                    len(board_state.attacks(square)) for square in board_state.pieces(piece, color)
                )
                mobility_score += piece_moves * piece_mobility_weights[piece]

            score += mobility_score * multiplier

        return score


    def evaluate_pawn_structure(self, board):
        """
        Evaluate pawn structure, applying penalties for isolated and doubled pawns.
        
        Args:
            board: A ChessBoard object.
        
        Returns:
            int: Pawn structure evaluation score.
        """

        board_state = board.get_board_state()

        score = 0


        # Evaluate for both colors

        for color in [True, False]:

            multiplier = 1 if color else -1

            pawns = board_state.pieces(chess.PAWN, color)

           

            # Check each file for isolated pawns

            for file in range(8):

                pawns_in_file = sum(1 for pawn in pawns

                                  if chess.square_file(pawn) == file)

                if pawns_in_file > 0:

                    # Check adjacent files

                    adjacent_pawns = sum(1 for pawn in pawns

                        if chess.square_file(pawn) in [file-1, file+1])

                    if adjacent_pawns == 0:

                        score -= 20 * multiplier  # Isolated pawn penalty

                       

                if pawns_in_file > 1:

                    score -= 10 * multiplier  # Doubled pawn penalty

                   

        return score
    
    
    def evaluate_king_safety(self, board):
        """
        Evaluate king safety by assessing the pawn shield.
        
        Args:
            board: A ChessBoard object.
        
        Returns:
            int: King safety evaluation score.
        """
         
        board_state = board.get_board_state()

        score = 0

       
        # Evaluate pawn shield for both kings

        for color in [True, False]:

            multiplier = 1 if color else -1

            king_square = board_state.king(color)

            if king_square is None:

                continue
   

            king_file = chess.square_file(king_square)

            king_rank = chess.square_rank(king_square)


            # Check pawn shield

            shield_score = 0

            for file in range(max(0, king_file - 1), min(8, king_file + 2)):

                shield_rank = king_rank + (1 if color else -1)

                shield_square = chess.square(file, shield_rank)

                if board_state.piece_at(shield_square) == chess.Piece(chess.PAWN, color):

                    shield_score += 10

                   

            score += shield_score * multiplier

           

        return score
    
    def minimax(self, board, depth, alpha, beta, maximizing_player):

        """
        Minimax implementation with alpha-beta pruning.
        
        Recursively searches moves and uses alpha-beta pruning to eliminate branches.
        
        Args:
            board: A ChessBoard object.
            depth (int): The search depth.
            alpha (float): Alpha value for pruning.
            beta (float): Beta value for pruning.
            maximizing_player (bool): True if the current turn is for the maximizing player.
        
        Returns:
            tuple: (best_score, best_move)
        """

        legal_moves = board.get_legal_moves()
        board_state = board.get_board_state()  # Current position

        # Base case: if depth is 0 or game is over, evaluate the board
        if depth == 0 or board.is_game_over():

            return self.evaluate_position(board), None



       # best_move = None

        if maximizing_player:
            best_move = None
            max_eval = float('-inf')

            for move in legal_moves:

                board_state.push(move)

                eval, _ = self.minimax(board, depth - 1, alpha, beta, False)

                board_state.pop()

                if eval > max_eval:

                    max_eval = eval

                    best_move = move
            
                alpha = max(alpha, eval)

                if beta <= alpha:
                    break

            # Returing max_eval & best move

            return (max_eval, best_move)

        else:

            min_eval = float('inf')
            best_move = None

            for move in legal_moves:

                board_state.push(move)

                eval, _ = self.minimax(board, depth - 1, alpha, beta, True)

                board_state.pop()

                if eval < min_eval:

                    min_eval = eval

                    best_move = move

                # Alpha & Beta Implementations 
                beta = min(beta, eval)

                if beta <= alpha:
                    break

            # Returing max_eval & best move

            return (min_eval, best_move)


    def get_move(self, board):
        
        """
        Main method to select the best move.
        
        Uses the minimax search with a preset depth (e.g., 3).
        
        Args:
            board: A ChessBoard object.
        
        Returns:
            chess.Move: The best move found.
        """

        board_state = board.get_board_state()
        
        _, best_move = self.minimax(board, depth=3, alpha=float('-inf'), beta=float('inf'), maximizing_player=board_state.turn)


        return best_move

    def get_game_phase(board):

        """
        Returns a value between 0 (endgame) and 256 (opening) based on remaining material.
        
        Args:
            board: A ChessBoard object.
        
        Returns:
            int: The game phase value.
        """

        piece_values = {
        chess.KNIGHT: 320, chess.BISHOP: 330,
        chess.ROOK: 500, chess.QUEEN: 900
        }
        
        npm = 0  # Non-pawn material

        for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:

            npm += len(board.pieces(piece_type, True)) * piece_values[piece_type]

            npm += len(board.pieces(piece_type, False)) * piece_values[piece_type]

    

        return min(npm, 256)



def interpolate(mg_score, eg_score, phase):

    """
    Interpolate between middlegame and endgame scores based on game phase.
    
    Args:
        mg_score (int): Middlegame score.
        eg_score (int): Endgame score.
        phase (int): Game phase value.
    
    Returns:
        int: The interpolated evaluation score.
    """

    return ((mg_score * phase) + (eg_score * (256 - phase))) // 256