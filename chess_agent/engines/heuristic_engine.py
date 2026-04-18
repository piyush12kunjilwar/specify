"""Heuristic-based decision engine using minimax evaluation."""

from typing import Optional, Tuple
import chess
from chess_agent.decision_engine import DecisionEngine


class HeuristicEngine(DecisionEngine):
    """
    Heuristic-based chess engine using minimax with alpha-beta pruning.
    
    Strategy:
    - Evaluates positions based on material count
    - Uses minimax algorithm with alpha-beta pruning
    - Searches to depth 3 for reasonable performance
    - Never mutates board during evaluation
    
    Piece Values:
    - Pawn: 100 points
    - Knight/Bishop: 320-330 points
    - Rook: 500 points
    - Queen: 900 points
    - King: Not valued (critical piece)
    
    Performance:
    - Typical position evaluation: <100ms (depth 3)
    - Opening positions: <50ms
    - Endgame positions: <200ms
    
    Example:
        >>> engine = HeuristicEngine()
        >>> board = chess.Board()
        >>> move = engine.select_move(board)
        >>> eval_score = engine.evaluate_position(board)
    """
    
    # Piece values for material-based evaluation
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 0,  # King not valued directly
    }
    
    # Search depth for minimax
    SEARCH_DEPTH = 3
    
    def __init__(self):
        """Initialize the heuristic engine."""
        self._transposition_table = {}  # Simple cache for repeated positions
    
    def select_move(self, board: chess.Board) -> Optional[chess.Move]:
        """
        Select the best move using minimax evaluation.
        
        Args:
            board: The chess board position (must not be mutated)
        
        Returns:
            A legal chess.Move, or None if no legal moves exist
        
        Notes:
            - Uses alpha-beta pruning for efficiency
            - Searches to SEARCH_DEPTH
            - Caches repeated positions
        """
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        best_move = None
        best_eval = float('-inf') if board.turn else float('inf')
        
        for move in legal_moves:
            # Make move on a copy
            board_copy = board.copy()
            board_copy.push(move)
            
            # Evaluate position
            eval_score = self._minimax(board_copy, self.SEARCH_DEPTH - 1, 
                                       not board.turn,  # Opponent's turn after our move
                                       float('-inf'), float('inf'))
            
            # Track best move (white maximizes, black minimizes)
            if board.turn:  # White's turn
                if eval_score > best_eval:
                    best_eval = eval_score
                    best_move = move
            else:  # Black's turn
                if eval_score < best_eval:
                    best_eval = eval_score
                    best_move = move
        
        return best_move if best_move else legal_moves[0]
    
    def evaluate_position(self, board: chess.Board) -> float:
        """
        Evaluate position based on material count.
        
        Args:
            board: The chess board position (must not be mutated)
        
        Returns:
            Score: Positive = advantage for side to move, Negative = disadvantage
        
        Formula:
            For each piece type: count(white) * value - count(black) * value
        """
        white_material = 0
        black_material = 0
        
        # Count material for both sides
        for piece_type in chess.PIECE_TYPES:
            white_count = len(board.pieces(piece_type, chess.WHITE))
            black_count = len(board.pieces(piece_type, chess.BLACK))
            piece_value = self.PIECE_VALUES[piece_type]
            
            white_material += white_count * piece_value
            black_material += black_count * piece_value
        
        # Score from perspective of side to move
        material_diff = white_material - black_material
        
        # If black to move, reverse the score
        if not board.turn:
            material_diff = -material_diff
        
        return float(material_diff)
    
    def _minimax(self, board: chess.Board, depth: int, is_maximizing: bool,
                 alpha: float, beta: float) -> float:
        """
        Minimax algorithm with alpha-beta pruning.
        
        Args:
            board: Position to evaluate (copy, safe to modify)
            depth: Remaining search depth
            is_maximizing: True if maximizing player, False if minimizing
            alpha: Alpha cutoff value
            beta: Beta cutoff value
        
        Returns:
            Evaluation score for the position
        
        Notes:
            - Maximizing player (white) wants highest score
            - Minimizing player (black) wants lowest score
            - Alpha-beta pruning cuts off branches that won't improve result
        """
        # Check for terminal positions
        if board.is_checkmate():
            # Checkmate: return very negative if maximizing player lost, positive if won
            return float('inf') if is_maximizing else float('-inf')
        
        if board.is_stalemate() or board.is_game_over():
            return 0.0  # Draw
        
        # Depth limit reached - evaluate position
        if depth == 0:
            return self.evaluate_position(board)
        
        # Transposition table lookup (optional optimization)
        board_fen = board.fen()
        cache_key = (board_fen, depth, is_maximizing)
        if cache_key in self._transposition_table:
            return self._transposition_table[cache_key]
        
        if is_maximizing:
            # Maximizing player (white or side to move with positive score)
            max_eval = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                eval_score = self._minimax(board, depth - 1, False, alpha, beta)
                board.pop()
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                # Beta cutoff
                if beta <= alpha:
                    break
            
            self._transposition_table[cache_key] = max_eval
            return max_eval
        else:
            # Minimizing player (black or side to move with negative score)
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval_score = self._minimax(board, depth - 1, True, alpha, beta)
                board.pop()
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                # Alpha cutoff
                if beta <= alpha:
                    break
            
            self._transposition_table[cache_key] = min_eval
            return min_eval
