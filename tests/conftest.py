"""Pytest configuration and shared fixtures."""

import pytest
import chess


@pytest.fixture
def starting_board():
    """Return the starting position FEN string."""
    return "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


@pytest.fixture
def sample_positions():
    """Return a dictionary of test positions for various scenarios."""
    return {
        "starting": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "after_1_e4": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
        "checkmate_fool_mate": "rnbqkbnr/pppp1ppp/8/4p3/6PP/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1",
        "stalemate_position": "k7/8/8/8/8/8/8/K6R w - - 0 1",
        "en_passant_available": "rnbqkbnr/ppppp1pp/8/4Pp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 3",
        "castling_kingside_available": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1",
    }
