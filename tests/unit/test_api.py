"""Unit tests for ChessAgent - high-level API."""

import pytest
import chess
from chess_agent.api import ChessAgent
from chess_agent.engines import HeuristicEngine
from chess_agent.decision_engine import DecisionEngine


class DummyEngine(DecisionEngine):
    """Dummy engine that always returns first legal move."""
    
    def select_move(self, board):
        """Return first legal move."""
        legal_moves = list(board.legal_moves)
        return legal_moves[0] if legal_moves else None
    
    def evaluate_position(self, board):
        """Return dummy evaluation."""
        return 0.0


class TestChessAgentInitialization:
    """Tests for ChessAgent initialization."""
    
    def test_init_default_engine(self):
        """Test initialization with default engine."""
        agent = ChessAgent()
        assert agent is not None
        assert agent.get_engine_info()["name"] == "HeuristicEngine"
    
    def test_init_custom_engine(self):
        """Test initialization with custom engine."""
        engine = DummyEngine()
        agent = ChessAgent(engine=engine)
        
        assert agent.get_engine_info()["name"] == "DummyEngine"
    
    def test_init_custom_fen(self):
        """Test initialization with custom starting position."""
        custom_fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
        agent = ChessAgent(fen=custom_fen)
        
        assert agent.get_board_fen() == custom_fen


class TestChessAgentMoveExecution:
    """Tests for playing moves."""
    
    def test_play_move_valid(self):
        """Test playing a valid move."""
        agent = ChessAgent()
        
        result = agent.play_move("e4")
        assert result is True
        assert "e4" in agent.get_board_fen()
    
    def test_play_move_invalid(self):
        """Test that invalid move returns False."""
        agent = ChessAgent()
        
        result = agent.play_move("e2e5")  # Pawn can't move 3 squares
        assert result is False
    
    def test_play_move_uci_notation(self):
        """Test playing move in UCI notation."""
        agent = ChessAgent()
        
        result = agent.play_move("e2e4")
        assert result is True
    
    def test_play_move_san_notation(self):
        """Test playing move in SAN notation."""
        agent = ChessAgent()
        
        result = agent.play_move("e4")
        assert result is True
    
    def test_play_move_after_game_over(self):
        """Test that moves are rejected after game ends."""
        agent = ChessAgent()
        agent._game._result = "1-0"
        
        result = agent.play_move("e4")
        assert result is False


class TestChessAgentBoardAccess:
    """Tests for board access methods."""
    
    def test_get_board(self):
        """Test getting board as chess.Board object."""
        agent = ChessAgent()
        
        board = agent.get_board()
        assert isinstance(board, chess.Board)
        assert len(list(board.legal_moves)) == 20
    
    def test_get_board_fen(self):
        """Test getting FEN notation."""
        agent = ChessAgent()
        
        fen = agent.get_board_fen()
        assert "rnbqkbnr" in fen
        assert "pppppppp" in fen
    
    def test_get_legal_moves(self):
        """Test getting legal moves."""
        agent = ChessAgent()
        
        moves = agent.get_legal_moves()
        assert len(moves) == 20
        assert all(isinstance(m, chess.Move) for m in moves)
    
    def test_get_legal_moves_san(self):
        """Test getting legal moves in SAN notation."""
        agent = ChessAgent()
        
        moves = agent.get_legal_moves_san()
        assert len(moves) == 20
        assert all(isinstance(m, str) for m in moves)
        assert "e4" in moves or "a3" in moves or "Nf3" in moves


class TestChessAgentAgentMoves:
    """Tests for agent move selection and execution."""
    
    def test_get_best_move(self):
        """Test getting best move without executing it."""
        agent = ChessAgent()
        
        best_move = agent.get_best_move()
        assert best_move in agent.get_legal_moves()
    
    def test_get_best_move_doesnt_modify_board(self):
        """Test that get_best_move doesn't modify the board."""
        agent = ChessAgent()
        original_fen = agent.get_board_fen()
        
        agent.get_best_move()
        
        assert agent.get_board_fen() == original_fen
    
    def test_play_agent_move(self):
        """Test executing agent's best move."""
        agent = ChessAgent()
        
        move_san = agent.play_agent_move()
        assert move_san is not None
        assert isinstance(move_san, str)
    
    def test_play_agent_move_modifies_board(self):
        """Test that play_agent_move modifies the board."""
        agent = ChessAgent()
        original_fen = agent.get_board_fen()
        
        agent.play_agent_move()
        
        assert agent.get_board_fen() != original_fen
    
    def test_play_agent_move_after_game_over(self):
        """Test that agent move is rejected after game ends."""
        agent = ChessAgent()
        agent._game._result = "1-0"
        
        with pytest.raises(ValueError):
            agent.play_agent_move()


class TestChessAgentGameStatus:
    """Tests for game status tracking."""
    
    def test_is_game_over_initially_false(self):
        """Test that game is not over initially."""
        agent = ChessAgent()
        
        assert agent.is_game_over() is False
    
    def test_get_result_initially_none(self):
        """Test that result is None initially."""
        agent = ChessAgent()
        
        assert agent.get_result() is None
    
    def test_is_game_over_after_result(self):
        """Test that game is over when result is set."""
        agent = ChessAgent()
        agent._game._result = "1-0"
        
        assert agent.is_game_over() is True
        assert agent.get_result() == "1-0"


class TestChessAgentReset:
    """Tests for game reset."""
    
    def test_reset_clears_game(self):
        """Test that reset returns to starting position."""
        agent = ChessAgent()
        original_fen = agent.get_board_fen()
        
        agent.play_move("e4")
        agent.reset()
        
        assert agent.get_board_fen() == original_fen
        assert agent.is_game_over() is False
    
    def test_reset_clears_result(self):
        """Test that reset clears the result."""
        agent = ChessAgent()
        agent._game._result = "1-0"
        
        agent.reset()
        
        assert agent.get_result() is None


class TestChessAgentEngineSwapping:
    """Tests for engine substitution."""
    
    def test_switch_engine(self):
        """Test switching to a different engine."""
        agent = ChessAgent()
        original_engine = agent.get_engine_info()["name"]
        
        agent.switch_engine(DummyEngine())
        
        assert agent.get_engine_info()["name"] == "DummyEngine"
        assert agent.get_engine_info()["name"] != original_engine
    
    def test_switch_engine_affects_future_moves(self):
        """Test that switching engine affects move selection."""
        agent = ChessAgent()
        
        agent.switch_engine(DummyEngine())
        move = agent.get_best_move()
        
        assert move in agent.get_legal_moves()


class TestChessAgentMoveHistory:
    """Tests for move history tracking."""
    
    def test_move_history_empty_initially(self):
        """Test that move history is empty initially."""
        agent = ChessAgent()
        
        history = agent.get_move_history()
        assert len(history) == 0
    
    def test_move_history_tracked(self):
        """Test that moves are tracked in history."""
        agent = ChessAgent()
        
        agent.play_move("e4")
        agent.play_move("e5")
        
        history = agent.get_move_history()
        assert len(history) == 2
        assert history[0] == ("e2e4", "e4")
        assert history[1] == ("e7e5", "e5")


class TestChessAgentEngineInfo:
    """Tests for engine information."""
    
    def test_get_engine_info_has_required_fields(self):
        """Test that engine info contains required fields."""
        agent = ChessAgent()
        
        info = agent.get_engine_info()
        assert "name" in info
        assert "type" in info
    
    def test_get_engine_info_correct_type(self):
        """Test that engine info reflects current engine type."""
        engine = DummyEngine()
        agent = ChessAgent(engine=engine)
        
        info = agent.get_engine_info()
        assert info["type"] == "DummyEngine"
        assert info["name"] == "DummyEngine"


class TestChessAgentIntegration:
    """Integration tests for full game scenarios."""
    
    def test_play_simple_game(self):
        """Test playing a simple game sequence."""
        agent = ChessAgent()
        
        # Play a few moves
        assert agent.play_move("e4") is True
        assert agent.play_agent_move() is not None
        assert agent.play_move("e5") is True
        assert agent.play_agent_move() is not None
        
        assert agent.is_game_over() is False
        assert len(agent.get_move_history()) == 4
    
    def test_game_through_completion(self):
        """Test game can reach completion."""
        agent = ChessAgent()
        
        # Play moves until game ends (may take a while in real game)
        # For now, just verify the game loop works
        for _ in range(10):
            if agent.is_game_over():
                break
            
            agent.play_move(agent.get_legal_moves_san()[0])
            
            if not agent.is_game_over():
                agent.play_agent_move()
