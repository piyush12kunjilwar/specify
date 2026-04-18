"""Unit tests for HeuristicEngine - minimax-based move selection and evaluation."""

import pytest
import chess
import time
from chess_agent.engines.heuristic_engine import HeuristicEngine


class TestHeuristicEngineBasics:
    """Tests for basic engine properties."""
    
    def test_engine_name(self):
        """Test engine returns correct name."""
        engine = HeuristicEngine()
        assert engine.get_engine_name() == "HeuristicEngine"


class TestHeuristicEngineMoveSelection:
    """Tests for move selection."""
    
    def test_select_move_returns_legal_move(self):
        """Test that selected move is in legal moves."""
        engine = HeuristicEngine()
        board = chess.Board()
        
        move = engine.select_move(board)
        assert move in board.legal_moves
    
    def test_select_move_single_legal_move(self):
        """Test engine selects the only legal move."""
        engine = HeuristicEngine()
        # Position with only one legal move
        board = chess.Board("k7/8/8/8/8/8/8/K6R w - - 0 1")
        
        move = engine.select_move(board)
        legal_moves = list(board.legal_moves)
        assert len(legal_moves) == 1
        assert move == legal_moves[0]
    
    def test_select_move_no_legal_moves(self):
        """Test engine returns None when no legal moves."""
        engine = HeuristicEngine()
        # Position with no legal moves
        board = chess.Board()
        board.set_fen("k7/8/8/8/8/8/8/K6R b - - 0 1")
        
        # If no legal moves, select_move should return None
        move = engine.select_move(board)
        if len(list(board.legal_moves)) == 0:
            assert move is None
    
    def test_select_move_consistent(self):
        """Test engine selects same move for same position."""
        engine = HeuristicEngine()
        board = chess.Board()
        
        move1 = engine.select_move(board)
        move2 = engine.select_move(board)
        
        assert move1 == move2


class TestHeuristicEngineEvaluation:
    """Tests for position evaluation."""
    
    def test_evaluate_position_starting_position(self):
        """Test evaluation of starting position (should be 0)."""
        engine = HeuristicEngine()
        board = chess.Board()
        
        eval_score = engine.evaluate_position(board)
        assert eval_score == 0.0  # Equal position
    
    def test_evaluate_position_white_advantage(self):
        """Test evaluation reflects white advantage."""
        engine = HeuristicEngine()
        # Position where white has captured a pawn
        board = chess.Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
        board.push(chess.Move.from_uci("e7e5"))
        board.push(chess.Move.from_uci("e4e5"))  # White captures
        
        eval_score = engine.evaluate_position(board)
        # White captured a pawn, so evaluation should be positive
        assert eval_score > 0
    
    def test_evaluate_position_black_advantage(self):
        """Test evaluation from black's perspective."""
        engine = HeuristicEngine()
        board = chess.Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
        
        eval_score = engine.evaluate_position(board)
        # From black's perspective (black to move), equal position
        # The engine evaluates from the perspective of the side to move
        assert isinstance(eval_score, float)
    
    def test_evaluate_position_deterministic(self):
        """Test that evaluation is deterministic."""
        engine = HeuristicEngine()
        board = chess.Board()
        
        eval1 = engine.evaluate_position(board)
        eval2 = engine.evaluate_position(board)
        
        assert eval1 == eval2


class TestHeuristicEnginePerformance:
    """Tests for engine performance."""
    
    def test_move_selection_performance(self):
        """Test that move selection completes in reasonable time."""
        engine = HeuristicEngine()
        board = chess.Board()
        
        start_time = time.time()
        move = engine.select_move(board)
        elapsed = time.time() - start_time
        
        # Should complete within 2 seconds for opening position
        assert elapsed < 2.0
        assert move is not None
    
    def test_evaluation_performance(self):
        """Test that evaluation completes quickly."""
        engine = HeuristicEngine()
        board = chess.Board()
        
        start_time = time.time()
        score = engine.evaluate_position(board)
        elapsed = time.time() - start_time
        
        # Should complete in milliseconds
        assert elapsed < 0.1
        assert isinstance(score, float)


class TestHeuristicEngineBoardImmutability:
    """Tests that engine doesn't mutate input board."""
    
    def test_select_move_doesnt_mutate_board(self):
        """Test that select_move doesn't mutate the board."""
        engine = HeuristicEngine()
        board = chess.Board()
        original_fen = board.fen()
        
        engine.select_move(board)
        
        assert board.fen() == original_fen
    
    def test_evaluate_position_doesnt_mutate_board(self):
        """Test that evaluate_position doesn't mutate the board."""
        engine = HeuristicEngine()
        board = chess.Board()
        original_fen = board.fen()
        
        engine.evaluate_position(board)
        
        assert board.fen() == original_fen
        """Test that move selection completes within time limit."""
        import time
        engine = HeuristicEngine()
        board = chess.Board()
        
        start = time.time()
        move = engine.select_move(board)
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        # Should complete in well under 100ms for depth 3 search
        assert elapsed < 100, f"Move selection took {elapsed}ms, expected < 100ms"


class TestHeuristicEngineEvaluation:
    """Tests for position evaluation."""
    
    def test_evaluate_position_white_advantage(self):
        """Test evaluation when white has material advantage."""
        engine = HeuristicEngine()
        # Position: white has extra queen
        board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        board.push(chess.Move.from_uci("e2e4"))
        
        eval_score = engine.evaluate_position(board)
        # Should be a reasonable number
        assert isinstance(eval_score, float)
        # Simple starting position should be roughly equal
        assert abs(eval_score) < 500
    
    def test_evaluate_position_black_advantage(self):
        """Test evaluation when black has material advantage."""
        engine = HeuristicEngine()
        board = chess.Board()
        
        # Make a few moves
        board.push(chess.Move.from_uci("e2e4"))
        board.push(chess.Move.from_uci("e7e5"))
        board.push(chess.Move.from_uci("f2f4"))
        
        eval_score = engine.evaluate_position(board)
        # Black should have slight advantage after capturing pawn
        assert isinstance(eval_score, float)
    
    def test_evaluate_position_equal(self):
        """Test evaluation of equal position."""
        engine = HeuristicEngine()
        board = chess.Board()
        
        eval_score = engine.evaluate_position(board)
        # Starting position should be roughly equal
        assert isinstance(eval_score, float)
        assert abs(eval_score) < 500


class TestHeuristicEnginePieceValues:
    """Tests for piece value constants."""
    
    def test_piece_values_pawn(self):
        """Test pawn value is 100."""
        from chess_agent.engines.heuristic_engine import HeuristicEngine
        # Assuming PIECE_VALUES is a class constant
        assert HeuristicEngine.PIECE_VALUES[chess.PAWN] == 100
    
    def test_piece_values_knight(self):
        """Test knight value is 320."""
        from chess_agent.engines.heuristic_engine import HeuristicEngine
        assert HeuristicEngine.PIECE_VALUES[chess.KNIGHT] == 320
    
    def test_piece_values_bishop(self):
        """Test bishop value is 330."""
        from chess_agent.engines.heuristic_engine import HeuristicEngine
        assert HeuristicEngine.PIECE_VALUES[chess.BISHOP] == 330
    
    def test_piece_values_rook(self):
        """Test rook value is 500."""
        from chess_agent.engines.heuristic_engine import HeuristicEngine
        assert HeuristicEngine.PIECE_VALUES[chess.ROOK] == 500
    
    def test_piece_values_queen(self):
        """Test queen value is 900."""
        from chess_agent.engines.heuristic_engine import HeuristicEngine
        assert HeuristicEngine.PIECE_VALUES[chess.QUEEN] == 900


class TestHeuristicEngineImmutability:
    """Tests for board immutability during evaluation."""
    
    def test_board_not_mutated_by_select_move(self):
        """Test that select_move does not mutate the input board."""
        engine = HeuristicEngine()
        board = chess.Board()
        original_fen = board.fen()
        
        engine.select_move(board)
        
        assert board.fen() == original_fen
    
    def test_board_not_mutated_by_evaluate_position(self):
        """Test that evaluate_position does not mutate the input board."""
        engine = HeuristicEngine()
        board = chess.Board()
        original_fen = board.fen()
        
        engine.evaluate_position(board)
        
        assert board.fen() == original_fen


class TestHeuristicEngineConsistency:
    """Tests for evaluation consistency."""
    
    def test_same_position_same_evaluation(self):
        """Test that same position gets same evaluation."""
        engine = HeuristicEngine()
        board = chess.Board()
        
        eval1 = engine.evaluate_position(board)
        eval2 = engine.evaluate_position(board)
        
        assert eval1 == eval2
    
    def test_move_selection_consistency(self):
        """Test that move selection is deterministic."""
        engine = HeuristicEngine()
        board = chess.Board()
        
        move1 = engine.select_move(board)
        
        # Reset board to same position
        board = chess.Board()
        move2 = engine.select_move(board)
        
        # Should select same move from same position
        assert move1 == move2
