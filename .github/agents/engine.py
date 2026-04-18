import time
import chess
from abc import ABC, abstractmethod


class DecisionEngine(ABC):
    """
    Interface for move evaluation strategies.
    Supports swapping between Heuristic and future LLM engines.
    """
    @abstractmethod
    def get_best_move(self, board: chess.Board, time_limit: float = 1.9) -> chess.Move:
        pass


class HeuristicEngine(DecisionEngine):
    def __init__(self, depth: int = 3):
        self.depth = depth
        self.piece_values = {
            chess.PAWN: 10,
            chess.KNIGHT: 30,
            chess.BISHOP: 30,
            chess.ROOK: 50,
            chess.QUEEN: 90,
            chess.KING: 900
        }

    def evaluate(self, board: chess.Board) -> int:
        if board.is_checkmate():
            return -9999 if board.turn else 9999
        if board.is_game_over():
            return 0

        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                val = self.piece_values.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    score += val
                else:
                    score -= val
                    
        # Perspective evaluation (positive is good for current turn)
        return score if board.turn == chess.WHITE else -score

    def minimax(self, board: chess.Board, depth: int, alpha: int, beta: int, maximizing: bool, start_time: float, time_limit: float) -> int:
        if depth == 0 or board.is_game_over() or (time.time() - start_time) > time_limit:
            return self.evaluate(board)

        # Efficiency: Prune branches safely with Alpha-Beta
        if maximizing:
            max_eval = -float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta, False, start_time, time_limit)
                board.pop()
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta, True, start_time, time_limit)
                board.pop()
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, board: chess.Board, time_limit: float = 1.9) -> chess.Move:
        start_time = time.time()
        eval_board = board.copy()  # Rule II: Safe Board State Management
        
        best_move = None
        best_value = -float('inf')
        alpha = -float('inf')
        beta = float('inf')

        # Time limit constraints enforced continuously during the loop
        for move in eval_board.legal_moves:
            eval_board.push(move)
            board_val = self.minimax(eval_board, self.depth - 1, alpha, beta, False, start_time, time_limit)
            eval_board.pop()

            if board_val > best_value:
                best_value = board_val
                best_move = move

            if (time.time() - start_time) > time_limit:
                break

        if best_move is None:
            try:
                best_move = next(iter(board.legal_moves))
            except StopIteration:
                pass

        return best_move


class LLMEngine(DecisionEngine):
    """
    Decision engine that uses a Large Language Model to evaluate and select moves.
    Currently implements the prompt generation interface for future API integration.
    """
    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt or "You are an autonomous expert chess grandmaster."

    def generate_prompt(self, board: chess.Board) -> str:
        turn = "White" if board.turn == chess.WHITE else "Black"
        fen = board.fen()
        legal_moves = [board.san(move) for move in board.legal_moves]
        
        return (
            f"{self.system_prompt}\n"
            f"You are playing as {turn}.\n"
            f"The current board state in FEN notation is: {fen}\n"
            f"The list of legal moves you can make is: {', '.join(legal_moves)}\n\n"
            "Evaluate the board position and provide your best move.\n"
            "You MUST respond with ONLY the valid move in Standard Algebraic Notation (SAN) "
            "from the legal moves list."
        )

    def get_best_move(self, board: chess.Board, time_limit: float = 1.9) -> chess.Move:
        prompt = self.generate_prompt(board)
        # TODO: Implement the actual LLM API call here using `prompt`
        # Fallback to the first legal move so the interface contract is fulfilled during testing
        try:
            return next(iter(board.legal_moves))
        except StopIteration:
            return None