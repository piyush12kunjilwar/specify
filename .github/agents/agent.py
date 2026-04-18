import chess
from typing import Optional
from engine import DecisionEngine, HeuristicEngine

class ChessAgent:
    """
    Autonomous chess player that evaluates positions and manages rules.
    """
    def __init__(self, engine: Optional[DecisionEngine] = None):
        self.board = chess.Board()
        self.engine = engine or HeuristicEngine()
        self.history = []

    def make_move(self, move_str: str) -> bool:
        try:
            move = self.board.parse_san(move_str)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.history.append(move_str)
                return True
        except ValueError:
            pass
        return False

    def get_next_move(self) -> Optional[chess.Move]:
        if self.board.is_game_over():
            return None
        # Evaluate on an immutable copy
        return self.engine.get_best_move(self.get_board_state())

    def apply_agent_move(self) -> Optional[chess.Move]:
        move = self.get_next_move()
        if move:
            san_move = self.board.san(move)
            self.board.push(move)
            self.history.append(san_move)
        return move

    def get_board_state(self) -> chess.Board:
        # Rule II: Never mutate live game state accidentally
        return self.board.copy()
        
    def get_game_status(self) -> str:
        if self.board.is_checkmate():
            return "Checkmate"
        if self.board.is_stalemate():
            return "Stalemate"
        if self.board.is_insufficient_material():
            return "Draw (Insufficient Material)"
        if self.board.can_claim_threefold_repetition():
            return "Draw (Threefold Repetition)"
        if self.board.can_claim_fifty_moves():
            return "Draw (Fifty-Move Rule)"
        return "In Progress"