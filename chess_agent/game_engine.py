"""Game engine managing chess game lifecycle and move orchestration."""

from typing import Tuple, Optional
import chess
from chess_agent.board_manager import BoardManager
from chess_agent.decision_engine import DecisionEngine


class GameEngine:
    """
    Orchestrates chess game flow, coordinating board state and decision engine.
    
    Responsibilities:
    - Manage game lifecycle (ongoing, checkmate, stalemate, draws)
    - Handle human move input and validation
    - Trigger agent move selection and execution
    - Enforce turn alternation
    - Track game result
    
    Architecture:
    - BoardManager handles board state and move validation (pure data)
    - DecisionEngine handles move selection strategy (swappable)
    - GameEngine orchestrates the workflow
    
    Example:
        >>> manager = BoardManager()
        >>> engine = HeuristicEngine()
        >>> game = GameEngine(manager, engine)
        >>> success, msg = game.play_human_move("e4")
        >>> if success:
        ...     agent_move = game.play_agent_move()
    """
    
    def __init__(self, board_manager: BoardManager, decision_engine: DecisionEngine):
        """
        Initialize game engine with board state and decision strategy.
        
        Args:
            board_manager: BoardManager instance managing board state
            decision_engine: DecisionEngine instance for move selection
        """
        self._board = board_manager
        self._engine = decision_engine
        self._result: Optional[str] = None
    
    def play_human_move(self, move_str: str) -> Tuple[bool, str]:
        """
        Play a human move, validate it, and trigger agent response.
        
        Args:
            move_str: Move in SAN (e.g., "e4") or UCI notation (e.g., "e2e4")
        
        Returns:
            (success: bool, message: str)
            - True if move succeeded, False otherwise
            - Message describes outcome (error or confirmation)
        
        Raises:
            None - Always returns (bool, str)
        
        Example:
            >>> success, msg = game.play_human_move("e4")
            >>> if success:
            ...     print(f"Human moved: {msg}")
        """
        if self.is_game_over():
            return False, "Game is already over"
        
        # Parse the move
        move = self._board.parse_move(move_str)
        if not move:
            return False, f"Invalid move notation: {move_str}"
        
        # Validate and execute
        if not self._board.validate_move(move):
            return False, f"Illegal move: {move_str}"
        
        # Get SAN notation before making the move
        san_move = self._board.get_san_move(move)
        
        # Execute the move
        self._board.make_move(move)
        
        # Check if game ended
        self._check_game_over()
        
        if self.is_game_over():
            return True, f"Human moved {san_move}, game over"
        
        # Trigger agent move
        agent_move_san = self.play_agent_move()
        return True, f"Human played {san_move}, agent responds with {agent_move_san}"
    
    def play_agent_move(self) -> str:
        """
        Execute the agent's selected move.
        
        The agent receives only a copy of the board (safe for lookahead).
        The selected move is validated and applied to the actual board.
        
        Returns:
            The executed move in standard algebraic notation (e.g., "e4")
        
        Raises:
            ValueError: If agent cannot select a move (no legal moves)
        
        Example:
            >>> move_san = game.play_agent_move()
            >>> print(f"Agent moved: {move_san}")
        """
        if self.is_game_over():
            raise ValueError("Cannot play move - game is over")
        
        # Get board copy for engine (immutable for lookahead)
        board_copy = self._board.get_board_copy()
        
        # Engine selects move (doesn't mutate the copy)
        move = self._engine.select_move(board_copy)
        
        if not move:
            raise ValueError("Agent failed to select a valid move")
        
        # Get SAN notation before making the move (board must be in original state)
        san_move = self._board.get_san_move(move)
        
        # Execute on actual board
        if not self._board.make_move(move):
            raise ValueError("Agent selected illegal move")
        
        # Check termination
        self._check_game_over()
        
        # Return in SAN notation
        return san_move
    
    def _check_game_over(self) -> None:
        """
        Check if game has ended and update result.
        
        Checks for:
        - Checkmate (winner determined)
        - Stalemate (draw)
        - Insufficient material (draw)
        - Threefold repetition (draw)
        - 50-move rule (draw)
        """
        if self._result is not None:
            return  # Already over
        
        if self._board.is_checkmate():
            # Current player is checkmated - opponent wins
            if self._board.get_board_copy().turn:
                self._result = "0-1"  # Black wins (white to move but checkmated)
            else:
                self._result = "1-0"  # White wins (black to move but checkmated)
        elif self._board.is_stalemate():
            self._result = "1/2-1/2"  # Draw
        elif self._board.is_draw():
            self._result = "1/2-1/2"  # Draw (insufficient material, repetition, etc.)
    
    def is_game_over(self) -> bool:
        """
        Check if the game has ended.
        
        Returns:
            True if game is over (checkmate, stalemate, or draw), False otherwise
        
        Example:
            >>> while not game.is_game_over():
            ...     game.play_human_move("e4")
        """
        return self._result is not None
    
    def get_result(self) -> Optional[str]:
        """
        Get the game result.
        
        Returns:
            - "1-0" if white wins (black is checkmated)
            - "0-1" if black wins (white is checkmated)
            - "1/2-1/2" if draw (stalemate, insufficient material, repetition, 50-move rule)
            - None if game is still ongoing
        
        Example:
            >>> while not game.is_game_over():
            ...     game.play_human_move(input("Your move: "))
            >>> print(f"Result: {game.get_result()}")
        """
        return self._result
    
    def get_board_fen(self) -> str:
        """
        Get the current board position as FEN string.
        
        Returns:
            FEN notation string
        
        Example:
            >>> fen = game.get_board_fen()
            >>> print(fen)
        """
        return self._board.get_fen()
    
    def reset(self) -> None:
        """
        Reset game to starting position and clear result.
        
        Example:
            >>> game.reset()
            >>> assert not game.is_game_over()
        """
        self._board.reset()
        self._result = None
