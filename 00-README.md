# Chess Bot: AI-Driven Chess Engine

This repository contains my implementation of a chess bot built in Python. I developed a modular chess engine that uses search algorithms, evaluation functions, and self-play training to make intelligent move decisions. The bot leverages a custom minimax algorithm with alpha-beta pruning, an evaluation function that considers material, pawn structure, king safety, and mobility, and integrates an opening book for efficient early-game strategy.

## Repository Structure

- **`bot.py`**  
  Implements the `ChessBot` class, which:
  - Checks for book moves using an integrated opening book.
  - Evaluates board positions using several heuristics.
  - Uses a minimax algorithm with alpha-beta pruning to choose moves.
  
- **`book.py`**  
  Contains the `OpeningBook` class, which:
  - Loads an opening book (in Polyglot format or simple in-memory format).
  - Retrieves moves for a given board position using a simplified FEN string.
  
- **`trainer.py`**  
  Implements the `SelfPlayTrainer` class for self-play training:
  - Plays games between bot instances.
  - Analyzes game results and updates bot parameters based on performance.
  - Saves the best bot and training history.
  
- **`board.py`** (not shown here)  
  Provides the `ChessBoard` class as a wrapper around the python‑chess library for handling game state, legal moves, and board operations.

## Technologies Used

- **Language:** Python
- **Libraries:** python‑chess, random, time, json, copy
- **Development Tools:** VS Code, Git & GitHub
