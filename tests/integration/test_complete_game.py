"""Integration tests for complete chess games."""

import pytest
import chess
from chess_agent.board_manager import BoardManager
from chess_agent.game_engine import GameEngine
from chess_agent.engines.heuristic_engine import HeuristicEngine


class TestCompleteGameScenarios:
    """Tests for full game flows from start to finish."""
    
    def test_complete_game_white_wins(self):
        """Test playing through to white checkmate."""
        board_manager = BoardManager()
        engine = HeuristicEngine()
        game = GameEngine(board_manager, engine)
        
        # Play a mini-game toward white winning
        # Scholar's mate setup
        moves = ["e4", "e5", "Bc4", "Nc6", "Qh5", "Nf6", "Qxf7"]
        
        for move_san in moves:
            if not game.is_game_over():
                success, _ = game.play_human_move(move_san)
                if not success or game.is_game_over():
                    break
                if not game.is_game_over():
                    game.play_agent_move()
        
        # Check that game ended
        assert game.is_game_over() is True
        assert game.get_result() in ["1-0", "0-1", "1/2-1/2"]
    
    def test_complete_game_black_wins(self):
        """Test playing through to black checkmate."""
        board_manager = BoardManager()
        engine = HeuristicEngine()
        game = GameEngine(board_manager, engine)
        
        # Play a few moves of fool's mate setup
        moves = ["f3", "e5", "g4"]
        
        for move_san in moves:
            if not game.is_game_over():
                success, _ = game.play_human_move(move_san)
                if not success or game.is_game_over():
                    break
                if not game.is_game_over():
                    game.play_agent_move()
        
        # After fool's mate, game should be over
        assert game.is_game_over() is True
        result = game.get_result()
        assert result in ["1-0", "0-1", "1/2-1/2"]
    
    def test_complete_game_stalemate(self):
        """Test reaching stalemate position."""
        # Create a stalemate position directly
        stalemate_fen = "k7/8/8/8/8/8/8/K6R w - - 0 1"
        board_manager = BoardManager(stalemate_fen)
        engine = HeuristicEngine()
        game = GameEngine(board_manager, engine)
        
        # Position should already be stalemate
        assert game.is_game_over() is True
        assert game.get_result() == "1/2-1/2"
    
    def test_complete_game_insufficient_material(self):
        """Test reaching insufficient material draw."""
        # King vs King position
        kk_fen = "k7/8/8/8/8/8/8/K7 w - - 0 1"
        board_manager = BoardManager(kk_fen)
        engine = HeuristicEngine()
        game = GameEngine(board_manager, engine)
        
        # Position should be a draw
        assert game.is_game_over() is True
        assert game.get_result() == "1/2-1/2"
    
    def test_game_reset_mid_game(self):
        """Test resetting game after several moves."""
        board_manager = BoardManager()
        engine = HeuristicEngine()
        game = GameEngine(board_manager, engine)
        
        # Make several moves
        game.play_human_move("e4")
        game.play_agent_move()
        game.play_human_move("d4")
        
        # Reset
        game.reset()
        
        # Should be back to start
        assert game.get_board_fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        assert game.is_game_over() is False
        assert game.get_result() is None


class TestGameStability:
    """Tests for game stability and consistency."""
    
    def test_multiple_games_independent(self):
        """Test that multiple game instances don't interfere."""
        game1 = GameEngine(BoardManager(), HeuristicEngine())
        game2 = GameEngine(BoardManager(), HeuristicEngine())
        
        game1.play_human_move("e4")
        game1.play_agent_move()
        
        # game2 should still be at start
        assert game2.get_board_fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    
    def test_alternating_moves_maintain_position(self):
        """Test that positions stay synchronized during alternating moves."""
        board_manager = BoardManager()
        engine = HeuristicEngine()
        game = GameEngine(board_manager, engine)
        
        for i in range(5):  # 5 move pairs
            if game.is_game_over():
                break
            
            success1, _ = game.play_human_move("a3") if i % 2 == 0 else game.play_human_move("a6")
            if success1 and not game.is_game_over():
                game.play_agent_move()
