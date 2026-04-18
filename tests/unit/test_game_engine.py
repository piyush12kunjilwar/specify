"""Unit tests for GameEngine - game lifecycle and move execution."""

import pytest
import chess
from chess_agent.board_manager import BoardManager
from chess_agent.decision_engine import DecisionEngine
from chess_agent.game_engine import GameEngine


class MockDecisionEngine(DecisionEngine):
    """Mock decision engine for testing game engine."""
    
    def __init__(self, move_to_select=None):
        """Initialize with optional fixed move."""
        self.move_to_select = move_to_select
        self.calls = []
    
    def select_move(self, board):
        """Return predetermined move or first legal move."""
        self.calls.append(('select_move', board.fen()))
        if self.move_to_select:
            return self.move_to_select
        legal_moves = list(board.legal_moves)
        return legal_moves[0] if legal_moves else None
    
    def evaluate_position(self, board):
        """Return simple material evaluation."""
        self.calls.append(('evaluate_position', board.fen()))
        return 0.0


class TestGameEngineInitialization:
    """Tests for GameEngine initialization."""
    
    def test_game_init(self):
        """Test GameEngine initializes with board and engine."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        assert game is not None
        assert game.get_board_fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


class TestGameEngineHumanMoves:
    """Tests for human move execution."""
    
    def test_play_human_move_valid(self):
        """Test valid human move succeeds."""
        board_manager = BoardManager()
        engine = MockDecisionEngine(move_to_select=chess.Move.from_uci("e7e5"))
        game = GameEngine(board_manager, engine)
        
        success, msg = game.play_human_move("e4")
        assert success is True
        assert "e4" in board_manager.get_fen()
    
    def test_play_human_move_invalid_notation(self):
        """Test that invalid move notation is rejected."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        success, msg = game.play_human_move("invalid")
        assert success is False
        assert "Invalid" in msg or "invalid" in msg.lower()
    
    def test_play_human_move_illegal_move(self):
        """Test that illegal move is rejected."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        success, msg = game.play_human_move("e2e5")  # Illegal - pawn can't move 3 squares
        assert success is False
        assert "Illegal" in msg or "illegal" in msg.lower()
    
    def test_play_human_move_after_game_over(self):
        """Test that moves are rejected after game ends."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        # Manually set game as over
        game._result = "1-0"
        
        success, msg = game.play_human_move("e4")
        assert success is False
        assert "already over" in msg.lower()


class TestGameEngineAgentMoves:
    """Tests for agent move execution."""
    
    def test_play_agent_move_success(self):
        """Test agent successfully plays a move."""
        board_manager = BoardManager()
        engine = MockDecisionEngine(move_to_select=chess.Move.from_uci("e2e4"))
        game = GameEngine(board_manager, engine)
        
        move_san = game.play_agent_move()
        assert move_san == "e4"
        assert "e4" in board_manager.get_fen()
    
    def test_play_agent_move_after_game_over(self):
        """Test that agent move is rejected when game is over."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        game._result = "1-0"
        
        with pytest.raises(ValueError, match="already over"):
            game.play_agent_move()
    
    def test_play_agent_move_no_legal_moves(self):
        """Test that agent raises error if no legal moves."""
        board_manager = BoardManager()
        engine = MockDecisionEngine(move_to_select=None)
        game = GameEngine(board_manager, engine)
        
        with pytest.raises(ValueError, match="failed|no move"):
            game.play_agent_move()


class TestGameEngineGameStatus:
    """Tests for game status and result tracking."""
    
    def test_is_game_over_initially_false(self):
        """Test that game is not over at start."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        assert game.is_game_over() is False
    
    def test_get_result_initially_none(self):
        """Test that result is None at game start."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        assert game.get_result() is None
    
    def test_get_board_fen(self):
        """Test getting board as FEN string."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        fen = game.get_board_fen()
        assert "rnbqkbnr" in fen
        assert "pppppppp" in fen


class TestGameEngineReset:
    """Tests for game reset functionality."""
    
    def test_reset_clears_result(self):
        """Test that reset clears the game result."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        game._result = "1-0"
        game.reset()
        
        assert game.get_result() is None
        assert game.is_game_over() is False
    
    def test_reset_returns_to_start(self):
        """Test that reset returns to starting position."""
        board_manager = BoardManager()
        engine = MockDecisionEngine(move_to_select=chess.Move.from_uci("e7e5"))
        game = GameEngine(board_manager, engine)
        
        original_fen = game.get_board_fen()
        
        game.play_agent_move()
        game.reset()
        
        assert game.get_board_fen() == original_fen
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        success, message = game.play_human_move("e4")
        assert success is True
        assert isinstance(message, str)
    
    def test_play_human_move_invalid_format(self):
        """Test invalid move format is rejected."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        success, message = game.play_human_move("xyz")
        assert success is False
        assert isinstance(message, str)
    
    def test_play_human_move_illegal(self):
        """Test illegal move is rejected."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        success, message = game.play_human_move("e5")  # Illegal for white
        assert success is False
    
    def test_play_human_move_updates_board(self):
        """Test that board state changes after valid move."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        original_fen = game.get_board_fen()
        game.play_human_move("e4")
        new_fen = game.get_board_fen()
        
        assert original_fen != new_fen


class TestGameEngineAgentMoves:
    """Tests for agent move execution."""
    
    def test_play_agent_move(self):
        """Test agent selects and executes move."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        move_san = game.play_agent_move()
        assert isinstance(move_san, str)
        assert len(move_san) > 0
    
    def test_play_agent_move_updates_board(self):
        """Test that board state changes after agent move."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        original_fen = game.get_board_fen()
        game.play_agent_move()
        new_fen = game.get_board_fen()
        
        assert original_fen != new_fen


class TestGameEngineTurnAlternation:
    """Tests for turn alternation."""
    
    def test_game_alternation_white_then_black(self):
        """Test white moves, then black moves."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        # White's move
        game.play_human_move("e4")
        
        # Black's move (via agent)
        move_san = game.play_agent_move()
        assert isinstance(move_san, str)
    
    def test_game_alternation_black_then_white(self):
        """Test move sequence alternates correctly."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        # White moves
        game.play_human_move("e4")
        # Black moves
        game.play_agent_move()
        # White moves again
        success, _ = game.play_human_move("e5")
        assert success is True


class TestGameEngineCheckmate:
    """Tests for checkmate detection and game ending."""
    
    def test_checkmate_detection_white(self):
        """Test detection of white checkmate."""
        # Set up fool's mate position
        fool_mate_fen = "rnbqkbnr/pppp1ppp/8/4p3/6PP/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1"
        board_manager = BoardManager(fool_mate_fen)
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        assert game.is_game_over() is True
        assert game.get_result() == "0-1"  # Black wins
    
    def test_checkmate_detection_black(self):
        """Test detection of black checkmate."""
        # Scholars mate setup: 1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7#
        scholars_mate_fen = "rnbqkb1r/pppp1pQp/5n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4"
        board_manager = BoardManager(scholars_mate_fen)
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        assert game.is_game_over() is True
        assert game.get_result() == "1-0"  # White wins


class TestGameEngineStalemateDetection:
    """Tests for stalemate detection."""
    
    def test_stalemate_detection(self):
        """Test detection of stalemate."""
        stalemate_fen = "k7/8/8/8/8/8/8/K6R w - - 0 1"
        board_manager = BoardManager(stalemate_fen)
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        assert game.is_game_over() is True
        assert game.get_result() == "1/2-1/2"  # Draw


class TestGameEngineDrawDetection:
    """Tests for draw detection."""
    
    def test_draw_insufficient_material(self):
        """Test draw detection for insufficient material."""
        kk_fen = "k7/8/8/8/8/8/8/K7 w - - 0 1"
        board_manager = BoardManager(kk_fen)
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        assert game.is_game_over() is True
        assert game.get_result() == "1/2-1/2"


class TestGameEngineGameState:
    """Tests for game state queries."""
    
    def test_game_over_stops_further_moves(self):
        """Test that moves cannot be played after game ends."""
        fool_mate_fen = "rnbqkbnr/pppp1ppp/8/4p3/6PP/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1"
        board_manager = BoardManager(fool_mate_fen)
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        assert game.is_game_over() is True
        
        # Try to play a move - should fail
        success, _ = game.play_human_move("a3")
        assert success is False
    
    def test_is_game_over_false_at_start(self):
        """Test that game is not over at start."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        assert game.is_game_over() is False
    
    def test_is_game_over_true_at_end(self):
        """Test that game is over after checkmate."""
        fool_mate_fen = "rnbqkbnr/pppp1ppp/8/4p3/6PP/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1"
        board_manager = BoardManager(fool_mate_fen)
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        assert game.is_game_over() is True


class TestGameEngineResults:
    """Tests for game result reporting."""
    
    def test_get_result_none_ongoing(self):
        """Test that result is None during ongoing game."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        assert game.get_result() is None
    
    def test_get_result_checkmate(self):
        """Test result reporting for checkmate."""
        fool_mate_fen = "rnbqkbnr/pppp1ppp/8/4p3/6PP/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1"
        board_manager = BoardManager(fool_mate_fen)
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        result = game.get_result()
        assert result in ["1-0", "0-1", "1/2-1/2"]
    
    def test_get_result_draw(self):
        """Test result reporting for draw."""
        kk_fen = "k7/8/8/8/8/8/8/K7 w - - 0 1"
        board_manager = BoardManager(kk_fen)
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        assert game.get_result() == "1/2-1/2"


class TestGameEngineReset:
    """Tests for game reset."""
    
    def test_reset_clears_state(self):
        """Test that reset returns to starting position."""
        board_manager = BoardManager()
        engine = MockDecisionEngine()
        game = GameEngine(board_manager, engine)
        
        # Make some moves
        game.play_human_move("e4")
        game.play_agent_move()
        game.play_human_move("e5")
        
        # Reset
        game.reset()
        
        # Should be back to start
        assert game.get_board_fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        assert game.is_game_over() is False
        assert game.get_result() is None
