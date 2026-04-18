"""Programmatic Python API for the autonomous chess agent."""

from typing import List, Optional, Tuple
import chess
from chess_agent.board_manager import BoardManager
from chess_agent.game_engine import GameEngine
from chess_agent.decision_engine import DecisionEngine
from chess_agent.engines import HeuristicEngine


class ChessAgent:
    """
    High-level API for playing chess against an autonomous agent.
    
    This class provides a simple interface for programmatic interaction with
    the chess agent, suitable for integration with other applications.
    
    Example:
        >>> agent = ChessAgent()
        >>> agent.play_move("e4")
        >>> agent_move = agent.get_best_move()
        >>> agent.play_move(agent_move.uci())
        >>> print(agent.get_board())
    """
    
    def __init__(self, engine: Optional[DecisionEngine] = None, fen: str = None) -> None:
        """
        Initialize the chess agent.
        
        Args:
            engine: Decision engine instance (default: HeuristicEngine)
            fen: Starting position as FEN string (default: starting position)
        
        Example:
            >>> agent = ChessAgent(engine=HeuristicEngine())
            >>> agent = ChessAgent(fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
        """
        if fen is None:
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        
        self._board_manager = BoardManager(fen)
        self._engine = engine or HeuristicEngine()
        self._game = GameEngine(self._board_manager, self._engine)
    
    def play_move(self, move_str: str) -> bool:
        """
        Play a move in the game.
        
        Args:
            move_str: Move in SAN notation (e.g., "e4") or UCI notation (e.g., "e2e4")
        
        Returns:
            True if move was legal and executed, False otherwise
        
        Example:
            >>> agent = ChessAgent()
            >>> if agent.play_move("e4"):
            ...     print("Move successful")
            >>> else:
            ...     print("Illegal move")
        """
        if self._game.is_game_over():
            return False
        
        move = self._board_manager.parse_move(move_str)
        if not move or not self._board_manager.validate_move(move):
            return False
        
        self._board_manager.make_move(move)
        self._game._check_game_over()
        return True
    
    def get_best_move(self) -> Optional[chess.Move]:
        """
        Get the agent's best move for the current position.
        
        Does not execute the move - only returns the recommended move.
        
        Returns:
            A chess.Move object, or None if no legal moves exist
        
        Example:
            >>> agent = ChessAgent()
            >>> agent.play_move("e4")
            >>> best = agent.get_best_move()
            >>> if best:
            ...     print(f"Best move: {agent.get_board().san(best)}")
        """
        if self._game.is_game_over():
            return None
        
        board_copy = self._board_manager.get_board_copy()
        return self._engine.select_move(board_copy)
    
    def play_agent_move(self) -> Optional[str]:
        """
        Execute the agent's best move and return it in SAN notation.
        
        Returns:
            The executed move in standard algebraic notation (e.g., "e4"),
            or None if no legal moves exist
        
        Raises:
            ValueError: If game is already over
        
        Example:
            >>> agent = ChessAgent()
            >>> agent.play_move("e4")
            >>> agent_move = agent.play_agent_move()
            >>> print(f"Agent played: {agent_move}")
        """
        if self._game.is_game_over():
            raise ValueError("Cannot play move - game is already over")
        
        board_copy = self._board_manager.get_board_copy()
        move = self._engine.select_move(board_copy)
        
        if not move:
            return None
        
        # Get SAN notation before making the move
        san_notation = self._board_manager.get_san_move(move)
        
        # Now make the move
        self._board_manager.make_move(move)
        self._game._check_game_over()
        return san_notation
    
    def get_board(self) -> chess.Board:
        """
        Get a copy of the current board position.
        
        Returns:
            A chess.Board object representing the current position
        
        Example:
            >>> agent = ChessAgent()
            >>> board = agent.get_board()
            >>> print(board)
        """
        return self._board_manager.get_board_copy()
    
    def get_board_fen(self) -> str:
        """
        Get the current position as FEN notation.
        
        Returns:
            FEN string representation of the current position
        
        Example:
            >>> agent = ChessAgent()
            >>> fen = agent.get_board_fen()
            >>> print(fen)
        """
        return self._board_manager.get_fen()
    
    def get_legal_moves(self) -> List[chess.Move]:
        """
        Get all legal moves for the side to move.
        
        Returns:
            List of chess.Move objects
        
        Example:
            >>> agent = ChessAgent()
            >>> moves = agent.get_legal_moves()
            >>> print(f"Legal moves: {len(moves)}")
        """
        return self._board_manager.get_legal_moves()
    
    def get_legal_moves_san(self) -> List[str]:
        """
        Get all legal moves in standard algebraic notation.
        
        Returns:
            List of SAN notation strings (e.g., ["e4", "Nf3", "d4", ...])
        
        Example:
            >>> agent = ChessAgent()
            >>> moves = agent.get_legal_moves_san()
            >>> print(f"Available: {', '.join(moves[:5])}")
        """
        moves = self._board_manager.get_legal_moves()
        return [self._board_manager.get_san_move(m) for m in moves]
    
    def is_game_over(self) -> bool:
        """
        Check if the game has ended.
        
        Returns:
            True if game is over (checkmate, stalemate, or draw), False otherwise
        
        Example:
            >>> agent = ChessAgent()
            >>> while not agent.is_game_over():
            ...     agent.play_move(input("Move: "))
        """
        return self._game.is_game_over()
    
    def get_result(self) -> Optional[str]:
        """
        Get the game result.
        
        Returns:
            - "1-0" if white wins
            - "0-1" if black wins
            - "1/2-1/2" if draw
            - None if game is still ongoing
        
        Example:
            >>> agent = ChessAgent()
            >>> while not agent.is_game_over():
            ...     agent.play_move(input("Move: "))
            >>> print(agent.get_result())
        """
        return self._game.get_result()
    
    def reset(self) -> None:
        """
        Reset the game to the starting position.
        
        Example:
            >>> agent = ChessAgent()
            >>> # ... play some moves ...
            >>> agent.reset()
            >>> assert agent.get_board_fen() == agent.ChessAgent().get_board_fen()
        """
        self._board_manager.reset()
        self._game = GameEngine(self._board_manager, self._engine)
    
    def switch_engine(self, engine: DecisionEngine) -> None:
        """
        Switch to a different decision engine.
        
        Args:
            engine: A DecisionEngine instance
        
        Example:
            >>> from chess_agent.engines import HeuristicEngine
            >>> agent = ChessAgent()
            >>> agent.switch_engine(HeuristicEngine())
        """
        self._engine = engine
        self._game = GameEngine(self._board_manager, self._engine)
    
    def get_move_history(self) -> List[Tuple[str, str]]:
        """
        Get the move history as a list of (move_uci, move_san) tuples.
        
        Returns:
            List of tuples containing UCI and SAN notation for each move
        
        Example:
            >>> agent = ChessAgent()
            >>> agent.play_move("e4")
            >>> history = agent.get_move_history()
            >>> print(history)  # [('e2e4', 'e4')]
        """
        moves = self._board_manager.get_move_history()
        
        # Reconstruct board history to get correct SAN notation for each move
        result = []
        board = chess.Board()
        
        for move in moves:
            try:
                san = board.san(move)
                result.append((move.uci(), san))
                board.push(move)
            except:
                # Fallback if there's an issue
                result.append((move.uci(), move.uci()))
        
        return result
    
    def get_engine_info(self) -> dict:
        """
        Get information about the current decision engine.
        
        Returns:
            Dictionary with engine metadata
        
        Example:
            >>> agent = ChessAgent()
            >>> info = agent.get_engine_info()
            >>> print(f"Engine: {info['name']}")
        """
        return {
            "name": self._engine.get_engine_name(),
            "type": type(self._engine).__name__,
        }
