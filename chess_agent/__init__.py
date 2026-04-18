"""Autonomous Chess Agent - A modular chess playing system.

This package provides a complete chess playing system with:
- BoardManager: Safe board state management with immutability guarantees
- GameEngine: Chess game orchestration and turn management
- DecisionEngine: Abstract interface for swappable move selection strategies
- HeuristicEngine: Minimax-based move evaluation with alpha-beta pruning
- ChessAgent: High-level API for programmatic interaction
- CLI: Command-line interface for interactive play

Example:
    >>> from chess_agent import ChessAgent
    >>> agent = ChessAgent()
    >>> agent.play_move("e4")
    >>> agent.play_agent_move()
    >>> print(agent.get_board())
"""

from chess_agent.board_manager import BoardManager
from chess_agent.game_engine import GameEngine
from chess_agent.decision_engine import DecisionEngine
from chess_agent.engines import HeuristicEngine
from chess_agent.api import ChessAgent

__version__ = "0.1.0"
__all__ = [
    "BoardManager",
    "GameEngine",
    "DecisionEngine",
    "HeuristicEngine",
    "ChessAgent",
]
