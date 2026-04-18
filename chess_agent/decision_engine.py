"""Abstract decision engine interface for autonomous move selection."""

from abc import ABC, abstractmethod
from typing import Optional
import chess


class DecisionEngine(ABC):
    """
    Abstract base class for chess decision engines.
    
    A decision engine is responsible for evaluating chess positions and selecting
    moves based on its evaluation strategy. This abstract interface allows for
    multiple implementations (heuristic, LLM-based, etc.) without changing the
    core game logic.
    
    All implementations must:
    - Never mutate the input board during evaluation
    - Return legal moves from the current position
    - Return consistent evaluations for repeated positions
    
    Example:
        >>> from chess_agent.decision_engine import DecisionEngine
        >>> engine = HeuristicEngine()  # Concrete implementation
        >>> board = chess.Board()
        >>> move = engine.select_move(board)  # Returns a legal move or None
        >>> eval_score = engine.evaluate_position(board)  # Returns float score
    """
    
    @abstractmethod
    def select_move(self, board: chess.Board) -> Optional[chess.Move]:
        """
        Select the best move for the current position.
        
        Args:
            board: The chess board position (must not be mutated)
        
        Returns:
            A legal chess.Move object, or None if no legal moves exist
        
        Raises:
            None - must gracefully handle positions with no legal moves
        
        Contract:
            - Input board must not be mutated
            - Return value must be in board.legal_moves
            - Must return None if board.legal_moves is empty (checkmate/stalemate)
        """
        raise NotImplementedError("Subclasses must implement select_move()")
    
    @abstractmethod
    def evaluate_position(self, board: chess.Board) -> float:
        """
        Evaluate the current position numerically.
        
        Args:
            board: The chess board position (must not be mutated)
        
        Returns:
            A float score:
            - Positive: Advantage for side to move
            - Negative: Disadvantage for side to move
            - 0: Equal position
            - Typical range: [-30000, +30000] (can extend for mating positions)
        
        Contract:
            - Input board must not be mutated
            - Same position should return same evaluation (deterministic)
        """
        raise NotImplementedError("Subclasses must implement evaluate_position()")
    
    def get_engine_name(self) -> str:
        """
        Get the name of this decision engine.
        
        Returns:
            A string identifier for the engine (e.g., "HeuristicEngine")
        
        Note:
            This method has a default implementation that returns the class name.
            Subclasses can override for custom names.
        """
        return self.__class__.__name__
