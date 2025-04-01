import chess
import random
import time
import json
import copy
from board import ChessBoard

class SelfPlayTrainer:

    def init(self, bot_constructor, games_per_iteration=50, iterations=10):

        """

        Create a self-play trainer for chess bots

       

        Args:

            bot_constructor: Function that returns a new ChessBot instance

            games_per_iteration: Number of games to play in each training iteration

            iterations: Number of training iterations to run

        """

        self.bot_constructor = bot_constructor

        self.games_per_iteration = games_per_iteration

        self.iterations = iterations

        self.best_bot = bot_constructor()

        self.game_history = []

        self.performance_history = []

       

    def train(self):

        """Run the complete self-play training process"""

        for iteration in range(self.iterations):

            print(f"Starting training iteration {iteration+1}/{self.iterations}")

           

            # Create challenger bot with variations

            challenger_bot = self.create_challenger()

           

            # Play training games

            results = self.play_match(self.best_bot, challenger_bot)

           

            # Analyze results

            analysis = self.analyze_results(results)

            print(f"Iteration {iteration+1} results: {analysis}")

           

            # Update the best bot if challenger performed better

            self.update_best_bot(challenger_bot, analysis)

           

            # Store performance metrics

            self.performance_history.append({

                "iteration": iteration + 1,

                "timestamp": time.time(),

                "metrics": analysis

            })

           

        return self.best_bot
    
    def create_challenger(self):

        """Create a challenger bot with slightly modified parameters"""

        challenger = self.bot_constructor()

       

        # If our bot has tunable parameters, modify them slightly

        if hasattr(challenger, 'piece_values'):

            for piece in challenger.piece_values:

                # Random adjustment between 95% and 105% of current value

                challenger.piece_values[piece] *= random.uniform(0.95, 1.05)

       

        if hasattr(challenger, 'position_scores'):

            # Similar modifications for positional scores

            for piece in challenger.position_scores:

                for i in range(len(challenger.position_scores[piece])):

                    challenger.position_scores[piece][i] *= random.uniform(0.95, 1.05)

       

        # Modify other parameters as needed

        return challenger

   

    def play_match(self, bot1, bot2):

        """Play a series of games between two bots"""

        results = []

       

        for game_num in range(self.games_per_iteration):

            # Alternate colors for fairness

            if game_num % 2 == 0:

                white_bot, black_bot = bot1, bot2

                color_map = {1: "bot1", -1: "bot2", 0: "draw"}

            else:

                white_bot, black_bot = bot2, bot1

                color_map = {-1: "bot1", 1: "bot2", 0: "draw"}

           

            # Play a game

            board = ChessBoard()

            moves = []

            result_code = self.play_game(board, white_bot, black_bot, moves)

           

            # Record result

            winner = color_map[result_code]

            results.append({

                "game_num": game_num,

                "winner": winner,

                "moves": moves,

                "result_code": result_code

            })

           

            if (game_num + 1) % 10 == 0:

                print(f"Played {game_num + 1}/{self.games_per_iteration} games")

       

        return results

    def play_game(self, board, white_bot, black_bot, moves):

        """Play a single game between two bots, return the result code"""

        move_count = 0

        position_history = {}

       

        while not board.is_game_over():

            # Track positions for threefold repetition detection

            board_key = board.get_fen().split(' ')[0]  # Just piece positions

            position_history[board_key] = position_history.get(board_key, 0) + 1

           

            # Detect draws by repetition or 50-move rule

            if position_history[board_key] >= 3 or board.halfmove_clock >= 100:

                return 0  # Draw

           

            # Get current bot's move

            current_bot = white_bot if board.turn == chess.WHITE else black_bot

            try:

                move = current_bot.get_move(board)

                if move:

                    moves.append(move)

                    board.make_move(move)

                else:

                    # No legal moves (should be caught by is_game_over, but just in case)

                    break

            except Exception as e:

                print(f"Error during move calculation: {e}")

                # Forfeit the game if an error occurs

                return -1 if board.turn == chess.WHITE else 1

           

            move_count += 1

           

            # Implement a move limit to prevent infinite games

            if move_count > 200:

                return 0  # Draw by excessive moves

       

        # Determine game result

        if board.is_checkmate():

            return -1 if board.turn == chess.WHITE else 1  # Winner is opposite of current turn

        else:

            return 0  # Draw by stalemate, insufficient material, etc.
        
    def analyze_results(self, results):

        """Analyze the match results"""

        bot1_wins = sum(1 for r in results if r["winner"] == "bot1")

        bot2_wins = sum(1 for r in results if r["winner"] == "bot2")

        draws = sum(1 for r in results if r["winner"] == "draw")

       

        # Calculate performance metrics

        total_games = len(results)

        bot1_win_rate = bot1_wins / total_games

        bot2_win_rate = bot2_wins / total_games

        draw_rate = draws / total_games

       

        # Calculate average game length

        game_lengths = [len(r["moves"]) for r in results]

        avg_game_length = sum(game_lengths) / len(game_lengths) if game_lengths else 0

       

        return {

            "bot1_wins": bot1_wins,

            "bot2_wins": bot2_wins,

            "draws": draws,

            "bot1_win_rate": bot1_win_rate,

            "bot2_win_rate": bot2_win_rate,

            "draw_rate": draw_rate,

            "avg_game_length": avg_game_length

        }

   

    def update_best_bot(self, challenger, analysis):

        """Update the best bot if the challenger performed better"""

        # If challenger (bot2) won more than current best (bot1), adopt its parameters

        if analysis["bot2_win_rate"] > analysis["bot1_win_rate"]:

            print("Challenger performed better - updating best bot")

           

            # Copy challenger parameters to best bot

            if hasattr(challenger, 'piece_values') and hasattr(self.best_bot, 'piece_values'):

                self.best_bot.piece_values = copy.deepcopy(challenger.piece_values)

               

            if hasattr(challenger, 'position_scores') and hasattr(self.best_bot, 'position_scores'):

                self.best_bot.position_scores = copy.deepcopy(challenger.position_scores)

    def save_best_bot(self, filepath):

        """Save the best bot's parameters to a file"""

        params = {}

       

        # Save piece values if they exist

        if hasattr(self.best_bot, 'piece_values'):

            params['piece_values'] = self.best_bot.piece_values

           

        # Save position scores if they exist

        if hasattr(self.best_bot, 'position_scores'):

            params['position_scores'] = self.best_bot.position_scores

           

        # Save other parameters

       

        with open(filepath, 'w') as f:

            json.dump(params, f, indent=2)

   

    def save_training_history(self, filepath):

        """Save the training history to a file"""

        history = {

            "performance_history": self.performance_history,

            "game_history": self.game_history[-100:]  # Save only the last 100 games to save space

        }

       

        with open(filepath, 'w') as f:

            json.dump(history, f, indent=2)