"""Board state management and move validation for chess positions."""

from typing import List, Optional
import chess


class BoardManager:
    """
    Manages chess board state with safe move handling and immutability guarantees.
    
    Key responsibilities:
    - Maintain board state safely (no mutations during lookahead)
    - Validate moves before execution
    - Track move history
    - Detect game termination conditions
    - Support position analysis
    
    Board state is always safe for lookahead evaluation because:
    1. get_board_copy() returns a true deep copy for evaluation
    2. Board mutations only occur via make_move() with validation
    3. All read operations are non-destructive
    
    Example:
        >>> manager = BoardManager()
        >>> legal_moves = manager.get_legal_moves()
        >>> if manager.validate_move(legal_moves[0]):
        ...     manager.make_move(legal_moves[0])
    """
    
    def __init__(self, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        """
        Initialize board manager with a position.
        
        Args:
            fen: FEN string representing the position (default: starting position)
        
        Raises:
            ValueError: If FEN is invalid
        """
        try:
            self._board = chess.Board(fen)
        except ValueError as e:
            raise ValueError(f"Invalid FEN string: {fen}") from e
        
        self._move_history: List[chess.Move] = []
        self._position_history: List[str] = [fen]
    
    def get_board_copy(self) -> chess.Board:
        """
        Get a deep copy of the board for safe lookahead evaluation.
        
        CRITICAL: This is the ONLY way for decision engines to get board access.
        Modifications to the returned board do NOT affect the managed board.
        
        Returns:
            A deep copy of the chess.Board (safe to modify)
        
        Example:
            >>> copy = manager.get_board_copy()
            >>> copy.push(move)  # Safe - doesn't affect manager's board
            >>> copy.pop()
        """
        return self._board.copy()
    
    def get_legal_moves(self) -> List[chess.Move]:
        """
        Get all legal moves from the current position.
        
        Returns:
            List of legal chess.Move objects (empty list if no legal moves)
        
        Example:
            >>> moves = manager.get_legal_moves()
            >>> print(f"Available moves: {len(moves)}")
        """
        return list(self._board.legal_moves)
    
    def make_move(self, move: chess.Move) -> bool:
        """
        Execute a move on the board, updating state atomically.
        
        Args:
            move: The chess.Move to execute
        
        Returns:
            True if move was legal and executed, False otherwise
        
        Raises:
            None - Returns False for illegal moves
        
        Example:
            >>> move = chess.Move.from_uci("e2e4")
            >>> if manager.make_move(move):
            ...     print("Move executed")
        """
        if not self.validate_move(move):
            return False
        
        self._board.push(move)
        self._move_history.append(move)
        self._position_history.append(self._board.fen())
        return True
    
    def validate_move(self, move: chess.Move) -> bool:
        """
        Check if a move is legal without modifying the board.
        
        Args:
            move: The chess.Move to validate
        
        Returns:
            True if the move is legal, False otherwise
        
        Example:
            >>> move = chess.Move.from_uci("e2e4")
            >>> is_legal = manager.validate_move(move)
        """
        return move in self._board.legal_moves
    
    def is_checkmate(self) -> bool:
        """
        Check if the current position is checkmate.
        
        Returns:
            True if current side to move is checkmated
        
        Example:
            >>> if manager.is_checkmate():
            ...     print("Game over - checkmate!")
        """
        return self._board.is_checkmate()
    
    def is_stalemate(self) -> bool:
        """
        Check if the current position is stalemate.
        
        Returns:
            True if current side to move is stalemated (not in check but no legal moves)
        
        Example:
            >>> if manager.is_stalemate():
            ...     print("Game over - stalemate!")
        """
        return self._board.is_stalemate()
    
    def is_draw(self) -> bool:
        """
        Check if the current position is a draw.
        
        Covers:
        - Insufficient material (K vs K, K+N vs K, K+B vs K, etc.)
        - Threefold repetition
        - Fifty-move rule
        
        Returns:
            True if position is drawn
        
        Example:
            >>> if manager.is_draw():
            ...     print("Game over - draw!")
        """
        return self._board.is_game_over() and not self._board.is_checkmate() and not self._board.is_stalemate()
    
    def get_fen(self) -> str:
        """
        Get the current position as FEN string.
        
        Returns:
            FEN string representation of current position
        
        Example:
            >>> fen = manager.get_fen()
            >>> print(fen)
        """
        return self._board.fen()
    
    def parse_move(self, move_str: str) -> Optional[chess.Move]:
        """
        Parse a move in SAN or UCI notation to a chess.Move object.
        
        Args:
            move_str: Move in SAN notation (e.g., "e4", "Nf3", "O-O") or UCI ("e2e4")
        
        Returns:
            chess.Move object, or None if notation is invalid
        
        Example:
            >>> move = manager.parse_move("e4")
            >>> if move:
            ...     manager.make_move(move)
        """
        try:
            # Try UCI notation first (e.g., "e2e4")
            if len(move_str) >= 4 and move_str[0:2] in [sq.name for sq in chess.SQUARES]:
                try:
                    return chess.Move.from_uci(move_str)
                except ValueError:
                    pass
            
            # Try SAN notation (e.g., "e4", "Nf3", "O-O")
            return self._board.parse_san(move_str)
        except (ValueError, AttributeError):
            return None
    
    def get_move_history(self) -> List[chess.Move]:
        """
        Get the list of all moves played from the start position.
        
        Returns:
            A copy of the move history (modifications don't affect internal state)
        
        Example:
            >>> history = manager.get_move_history()
            >>> print(f"Moves played: {len(history)}")
        """
        return list(self._move_history)
    
    def get_san_move(self, move: chess.Move) -> str:
        """
        Convert a chess.Move to standard algebraic notation.
        
        Args:
            move: The chess.Move to convert
        
        Returns:
            SAN notation string (e.g., "e4", "Nf3", "O-O")
        
        Example:
            >>> move = chess.Move.from_uci("e2e4")
            >>> san = manager.get_san_move(move)
            >>> print(san)  # "e4"
        """
        return self._board.san(move)
    
    def reset(self) -> None:
        """
        Reset the board to the starting position and clear history.
        
        Example:
            >>> manager.reset()
            >>> assert len(manager.get_move_history()) == 0
        """
        self._board = chess.Board()
        self._move_history = []
        self._position_history = [self._board.fen()]
