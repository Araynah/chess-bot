# Chess Bot: AI-Driven Chess Engine

This repository contains my implementation of a chess bot built in Python. I developed a modular chess engine that leverages search algorithms, evaluation functions, and self-play training to make intelligent move decisions. The bot uses a custom minimax algorithm with alpha-beta pruning, an evaluation function that considers material, pawn structure, king safety, and mobility, and integrates an opening book for efficient early-game play.

---

## Repository Structure

- **`bot.py`**  
  Implements the `ChessBot` class that:
  - Checks for opening book moves via an integrated `OpeningBook`.
  - Evaluates board positions using multiple heuristics (material, pawn structure, king safety, mobility).
  - Uses a minimax search with alpha-beta pruning to select moves.

- **`book.py`**  
  Contains the `OpeningBook` class that:
  - Loads and manages an opening book (via Polyglot format or a simple in-memory approach).
  - Returns moves based on a simplified FEN string for the current position.

- **`board.py`**  
  Provides the `ChessBoard` class as a wrapper around the python‑chess library to:
  - Initialize and manage the chess board.
  - Return legal moves.
  - Execute moves and check game status.
  
- **`game.py`**  
  Implements the `ChessGame` class which:
  - Sets up a full chess game environment.
  - Integrates the board, players (both human and bot), and handles graphics with Pygame.
  - Converts SVG board representations to Pygame surfaces for display.
  
- **`human.py`**  
  Implements the `HumanPlayer` class that:
  - Allows a human user to interact with the game via GUI.
  - Converts mouse clicks to board coordinates.
  - Handles piece selection, move validation, and pawn promotion through clickable buttons.
  
- **`trainer.py`**  
  Provides a self-play framework via the `SelfPlayTrainer` class that:
  - Runs multiple training iterations with bots playing against each other.
  - Analyzes game results and adjusts bot evaluation parameters.
  - Saves the best bot parameters and training history.

- *(Other support files such as configuration files or additional assets may also be included.)*

---

## Technologies Used

- **Language:** Python  
- **Libraries:** python‑chess, pygame, cairosvg, PIL (Pillow), random, time, json, copy  
- **Development Tools:** VS Code, Git & GitHub
