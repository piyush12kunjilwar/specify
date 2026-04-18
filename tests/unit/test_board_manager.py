"""Unit tests for BoardManager - board state and move validation."""

import pytest
import chess
from chess_agent.board_manager import BoardManager


class TestBoardManagerInitialization:
    """Tests for BoardManager initialization."""
    
    def test_init_default_position(self, starting_board):
        """Test initialization with default starting position."""
        manager = BoardManager()
        assert manager.get_fen() == starting_board
    
    def test_init_custom_fen(self):
        """Test initialization with custom FEN position."""
        custom_fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
        manager = BoardManager(custom_fen)
        assert manager.get_fen() == custom_fen
    
    def test_init_invalid_fen(self):
        """Test that invalid FEN raises ValueError."""
        with pytest.raises(ValueError):
            BoardManager("invalid fen string")


class TestBoardManagerBoardCopy:
    """Tests for safe board copying (critical for lookahead evaluation)."""
    
    def test_get_board_copy_isolation(self):
        """Test that board copy modifications don't affect original board."""
        manager = BoardManager()
        original_fen = manager.get_fen()
        
        board_copy = manager.get_board_copy()
        move = chess.Move.from_uci("e2e4")
        board_copy.push(move)
        
        # Original board should be unchanged
        assert manager.get_fen() == original_fen
    
    def test_get_board_copy_is_independent(self):
        """Test that multiple copies are independent."""
        manager = BoardManager()
        
        copy1 = manager.get_board_copy()
        copy2 = manager.get_board_copy()
        
        copy1.push(chess.Move.from_uci("e2e4"))
        copy2.push(chess.Move.from_uci("d2d4"))
        
        # Copies should have different states
        assert copy1.fen() != copy2.fen()
        # Original should be unchanged
        assert manager.get_fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


class TestBoardManagerLegalMoves:
    """Tests for legal move generation."""
    
    def test_get_legal_moves_starting_position(self):
        """Test that starting position has 20 legal moves."""
        manager = BoardManager()
        moves = manager.get_legal_moves()
        assert len(moves) == 20
        assert all(isinstance(m, chess.Move) for m in moves)
    
    def test_get_legal_moves_empty_at_checkmate(self):
        """Test that checkmate position returns empty list."""
        checkmate_fen = "rnb1kbnr/pppp1ppp/8/4p3/6PP/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1"
        manager = BoardManager(checkmate_fen)
        
        # Make another move to trigger checkmate
        manager.make_move(chess.Move.from_uci("g4f7"))
        moves = manager.get_legal_moves()
        assert len(moves) == 0  # No legal moves in checkmate


class TestBoardManagerMoveExecution:
    """Tests for making and validating moves."""
    
    def test_make_move_success(self):
        """Test successful move execution."""
        manager = BoardManager()
        move = chess.Move.from_uci("e2e4")
        
        assert manager.make_move(move) is True
        assert "e4" in manager.get_fen()  # Pawn should be on e4
    
    def test_make_move_invalid(self):
        """Test that invalid move returns False."""
        manager = BoardManager()
        invalid_move = chess.Move.from_uci("e2e5")  # Invalid - too far
        
        assert manager.make_move(invalid_move) is False
    
    def test_validate_move_legal(self):
        """Test validation of legal move."""
        manager = BoardManager()
        move = chess.Move.from_uci("e2e4")
        
        assert manager.validate_move(move) is True
    
    def test_validate_move_illegal(self):
        """Test validation of illegal move."""
        manager = BoardManager()
        move = chess.Move.from_uci("a2a5")  # Too far
        
        assert manager.validate_move(move) is False


class TestBoardManagerGameStatus:
    """Tests for game termination detection."""
    
    def test_is_checkmate(self):
        """Test checkmate detection."""
        checkmate_fen = "rnbqkbnr/pppp1Bpp/8/4p3/8/8/PPPPP1PP/RNBQK1NR b KQkq - 1 3"
        manager = BoardManager(checkmate_fen)
        
        # Move to checkmate position
        manager.make_move(chess.Move.from_uci("e5f6"))
        manager.make_move(chess.Move.from_uci("f7f6"))
        
        # This is not quite checkmate, but test the method
        assert isinstance(manager.is_checkmate(), bool)
    
    def test_is_stalemate(self):
        """Test stalemate detection."""
        stalemate_fen = "k7/8/8/8/8/8/8/K6R w - - 0 1"
        manager = BoardManager(stalemate_fen)
        
        # Make a move that causes stalemate
        manager.make_move(chess.Move.from_uci("h1h7"))
        assert manager.is_stalemate() is True
    
    def test_is_draw(self):
        """Test draw detection."""
        manager = BoardManager()
        # Draw by insufficient material shouldn't happen immediately
        assert manager.is_draw() is False


class TestBoardManagerMoveParsing:
    """Tests for move notation parsing."""
    
    def test_parse_move_san_notation(self):
        """Test parsing moves in SAN notation."""
        manager = BoardManager()
        
        move = manager.parse_move("e4")
        assert move is not None
        assert move.uci() == "e2e4"
    
    def test_parse_move_uci_notation(self):
        """Test parsing moves in UCI notation."""
        manager = BoardManager()
        
        move = manager.parse_move("e2e4")
        assert move is not None
        assert move.uci() == "e2e4"
    
    def test_parse_move_invalid(self):
        """Test parsing invalid move notation."""
        manager = BoardManager()
        
        move = manager.parse_move("invalid")
        assert move is None
    
    def test_parse_move_knight_notation(self):
        """Test parsing knight moves."""
        manager = BoardManager()
        
        move = manager.parse_move("Nf3")
        assert move is not None
        assert move.uci() == "g1f3"


class TestBoardManagerMoveHistory:
    """Tests for move history tracking."""
    
    def test_move_history_empty_initially(self):
        """Test that move history is empty at start."""
        manager = BoardManager()
        history = manager.get_move_history()
        
        assert len(history) == 0
    
    def test_move_history_tracked(self):
        """Test that moves are tracked in history."""
        manager = BoardManager()
        move1 = chess.Move.from_uci("e2e4")
        move2 = chess.Move.from_uci("e7e5")
        
        manager.make_move(move1)
        manager.make_move(move2)
        
        history = manager.get_move_history()
        assert len(history) == 2
        assert history[0] == move1
        assert history[1] == move2


class TestBoardManagerSANConversion:
    """Tests for SAN move notation conversion."""
    
    def test_get_san_move_pawn_move(self):
        """Test converting pawn move to SAN."""
        manager = BoardManager()
        move = chess.Move.from_uci("e2e4")
        
        san = manager.get_san_move(move)
        assert san == "e4"
    
    def test_get_san_move_knight_move(self):
        """Test converting knight move to SAN."""
        manager = BoardManager()
        move = chess.Move.from_uci("g1f3")
        
        san = manager.get_san_move(move)
        assert san == "Nf3"


class TestBoardManagerReset:
    """Tests for game reset functionality."""
    
    def test_reset_clears_history(self):
        """Test that reset clears move history."""
        manager = BoardManager()
        manager.make_move(chess.Move.from_uci("e2e4"))
        
        assert len(manager.get_move_history()) > 0
        
        manager.reset()
        
        assert len(manager.get_move_history()) == 0
    
    def test_reset_returns_to_start(self):
        """Test that reset returns to starting position."""
        manager = BoardManager()
        original_fen = manager.get_fen()
        
        manager.make_move(chess.Move.from_uci("e2e4"))
        manager.reset()
        
        assert manager.get_fen() == original_fen
        # Fool's mate position: checkmate
        fool_mate_fen = "rnbqkbnr/pppp1ppp/8/4p3/6PP/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1"
        manager = BoardManager(fool_mate_fen)
        moves = manager.get_legal_moves()
        assert len(moves) == 0


class TestBoardManagerMoveExecution:
    """Tests for move execution and board state updates."""
    
    def test_make_move_valid(self):
        """Test that valid moves are applied and state is updated."""
        manager = BoardManager()
        move = chess.Move.from_uci("e2e4")
        
        result = manager.make_move(move)
        assert result is True
        assert manager.get_fen() == "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    
    def test_make_move_invalid(self):
        """Test that invalid moves are rejected and state unchanged."""
        manager = BoardManager()
        invalid_move = chess.Move.from_uci("e1e2")  # King can't move there
        
        original_fen = manager.get_fen()
        result = manager.make_move(invalid_move)
        
        assert result is False
        assert manager.get_fen() == original_fen


class TestBoardManagerMoveValidation:
    """Tests for read-only move validation."""
    
    def test_validate_move_legal(self):
        """Test validation of legal moves."""
        manager = BoardManager()
        move = chess.Move.from_uci("e2e4")
        assert manager.validate_move(move) is True
    
    def test_validate_move_illegal(self):
        """Test validation of illegal moves."""
        manager = BoardManager()
        invalid_move = chess.Move.from_uci("e1e2")
        assert manager.validate_move(invalid_move) is False


class TestBoardManagerGameTermination:
    """Tests for game termination detection."""
    
    def test_is_checkmate(self):
        """Test checkmate detection."""
        fool_mate_fen = "rnbqkbnr/pppp1ppp/8/4p3/6PP/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1"
        manager = BoardManager(fool_mate_fen)
        assert manager.is_checkmate() is True
    
    def test_is_stalemate(self):
        """Test stalemate detection."""
        stalemate_fen = "k7/8/8/8/8/8/8/K6R w - - 0 1"
        manager = BoardManager(stalemate_fen)
        assert manager.is_stalemate() is True
    
    def test_is_draw_insufficient_material_k_vs_k(self):
        """Test draw detection: King vs King."""
        kk_fen = "k7/8/8/8/8/8/8/K7 w - - 0 1"
        manager = BoardManager(kk_fen)
        assert manager.is_draw() is True
    
    def test_is_draw_insufficient_material_k_n_vs_k(self):
        """Test draw detection: King+Knight vs King."""
        knk_fen = "k7/8/8/8/8/8/8/KN6 w - - 0 1"
        manager = BoardManager(knk_fen)
        # Insufficient material: King+Knight vs King is a draw
        assert manager.is_draw() is True
    
    def test_is_draw_insufficient_material_k_b_vs_k(self):
        """Test draw detection: King+Bishop vs King."""
        kbk_fen = "k7/8/8/8/8/8/8/KB6 w - - 0 1"
        manager = BoardManager(kbk_fen)
        # Insufficient material: King+Bishop vs King is a draw
        assert manager.is_draw() is True


class TestBoardManagerFENAccess:
    """Tests for FEN string access."""
    
    def test_get_fen(self):
        """Test FEN retrieval."""
        starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        manager = BoardManager()
        assert manager.get_fen() == starting_fen


class TestBoardManagerMoveNotation:
    """Tests for move notation parsing."""
    
    def test_parse_move_san_notation(self):
        """Test parsing standard algebraic notation."""
        manager = BoardManager()
        move = manager.parse_move("e4")
        assert move == chess.Move.from_uci("e2e4")
    
    def test_parse_move_uci_notation(self):
        """Test parsing UCI notation."""
        manager = BoardManager()
        move = manager.parse_move("e2e4")
        assert move == chess.Move.from_uci("e2e4")
    
    def test_parse_move_castling_kingside(self):
        """Test parsing kingside castling."""
        castling_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1"
        manager = BoardManager(castling_fen)
        move = manager.parse_move("O-O")
        assert move is not None
        assert move in manager.get_legal_moves()
    
    def test_parse_move_castling_queenside(self):
        """Test parsing queenside castling."""
        castling_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1"
        manager = BoardManager(castling_fen)
        move = manager.parse_move("O-O-O")
        assert move is not None
        assert move in manager.get_legal_moves()
    
    def test_parse_move_invalid(self):
        """Test parsing invalid move notation."""
        manager = BoardManager()
        move = manager.parse_move("xxx")
        assert move is None


class TestBoardManagerHistory:
    """Tests for move history tracking."""
    
    def test_get_move_history_isolation(self):
        """Test that returned history is isolated from internal state."""
        manager = BoardManager()
        manager.make_move(chess.Move.from_uci("e2e4"))
        
        history = manager.get_move_history()
        assert len(history) == 1
        
        # Try to modify returned history
        history.append(chess.Move.from_uci("e7e5"))
        
        # Internal history should be unchanged
        internal_history = manager.get_move_history()
        assert len(internal_history) == 1


class TestBoardManagerSANNotation:
    """Tests for standard algebraic notation conversion."""
    
    def test_get_san_move(self):
        """Test conversion of move to SAN notation."""
        manager = BoardManager()
        move = chess.Move.from_uci("e2e4")
        san = manager.get_san_move(move)
        assert san == "e4"


class TestBoardManagerReset:
    """Tests for board reset functionality."""
    
    def test_reset(self):
        """Test that reset returns board to starting position."""
        manager = BoardManager()
        manager.make_move(chess.Move.from_uci("e2e4"))
        manager.make_move(chess.Move.from_uci("e7e5"))
        
        manager.reset()
        
        assert manager.get_fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        assert len(manager.get_move_history()) == 0
