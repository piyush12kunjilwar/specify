import unittest
import chess
from agent import ChessAgent
from engine import HeuristicEngine, LLMEngine

class TestChessAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ChessAgent()

    def test_initialization(self):
        self.assertEqual(self.agent.get_game_status(), "In Progress")
        self.assertIsNotNone(self.agent.get_board_state())

    def test_make_valid_move(self):
        self.assertTrue(self.agent.make_move("e4"))
        self.assertEqual(len(self.agent.board.move_stack), 1)

    def test_make_invalid_move(self):
        self.assertFalse(self.agent.make_move("invalid"))
        self.assertFalse(self.agent.make_move("e5"))  # Illegal for white initially
        
    def test_board_state_isolation(self):
        board = self.agent.get_board_state()
        board.push_san("e4")
        # Assert mutating the fetched board doesn't mutate the agent's internal state
        self.assertNotEqual(self.agent.get_board_state().fen(), board.fen())

    def test_checkmate_detection(self):
        # Execute a Fool's mate
        self.agent.make_move("f3")
        self.agent.make_move("e5")
        self.agent.make_move("g4")
        self.agent.make_move("Qh4#")
        self.assertEqual(self.agent.get_game_status(), "Checkmate")

    def test_en_passant(self):
        # Set up an en passant capture
        moves = ["e4", "a6", "e5", "d5"]
        for move in moves:
            self.agent.make_move(move)
        # White executes en passant capture
        self.assertTrue(self.agent.make_move("exd6"))
        self.assertEqual(len(self.agent.board.move_stack), 5)

    def test_castling(self):
        # Set up a kingside castle for White
        moves = ["e4", "e5", "Nf3", "Nc6", "Bc4", "Nf6"]
        for move in moves:
            self.agent.make_move(move)
        # White castles kingside
        self.assertTrue(self.agent.make_move("O-O"))
        self.assertEqual(len(self.agent.board.move_stack), 7)

    def test_pawn_promotion(self):
        # Set up a pawn promotion scenario with valid kings on board
        self.agent.board.set_fen("8/P7/8/8/8/8/8/K1k5 w - - 0 1")
        self.assertTrue(self.agent.make_move("a8=Q"))
        self.assertEqual(self.agent.board.piece_at(chess.A8).piece_type, chess.QUEEN)

    def test_swappable_engine(self):
        class DummyEngine(HeuristicEngine):
            def get_best_move(self, board, time_limit=2.0):
                return list(board.legal_moves)[0]  # Just pick the first legal move
        
        agent = ChessAgent(engine=DummyEngine())
        move = agent.get_next_move()
        self.assertIn(move, agent.board.legal_moves)

    def test_llm_engine_prompt_generation(self):
        engine = LLMEngine(system_prompt="Test System Prompt")
        # Using the pawn promotion setup to test string formulation
        board = chess.Board("8/P7/8/8/8/8/8/K1k5 w - - 0 1")
        prompt = engine.generate_prompt(board)
        
        self.assertIn("Test System Prompt", prompt)
        self.assertIn("You are playing as White.", prompt)
        self.assertIn("8/P7/8/8/8/8/8/K1k5 w - - 0 1", prompt)
        self.assertIn("a8=Q", prompt)  # Validates that legal moves populate in the prompt string

if __name__ == "__main__":
    unittest.main()