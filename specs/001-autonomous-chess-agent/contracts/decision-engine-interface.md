# Contract: DecisionEngine Interface

**Status**: Stable (core interface for swappable implementations)  
**Version**: 1.0.0  
**Location**: `chess_agent/decision_engine.py`

---

## Purpose

Define the interface contract for chess move selection strategies. This interface enables:
- Pluggable decision engines (heuristic, LLM-based, neural network-based)
- Engine substitution at runtime without changing core game logic
- Future extensions without API breakage

---

## Interface Specification

### Abstract Base Class

```python
from abc import ABC, abstractmethod
import chess
from typing import Optional

class DecisionEngine(ABC):
    """Abstract interface for chess move selection strategies."""
```

### Required Methods

#### 1. `select_move(board: chess.Board) → Optional[chess.Move]`

**Purpose**: Select the next move for the current player.

**Signature**:
```python
@abstractmethod
def select_move(self, board: chess.Board) -> Optional[chess.Move]:
    """
    Select next move given a board position.
    
    Contract (CRITICAL - Do not violate):
    - Input board MUST NOT be modified
    - Returned move MUST be in board.legal_moves
    - Returned move MUST be the best move according to engine logic
    - Must complete within 2 seconds for typical positions
    
    Args:
        board (chess.Board): Current position
        
    Returns:
        chess.Move: Selected move, or None if no legal moves exist (game over)
        
    Raises:
        None (no exceptions expected in normal use)
        
    Examples:
        >>> board = chess.Board()
        >>> engine = HeuristicEngine()
        >>> move = engine.select_move(board)
        >>> move in board.legal_moves
        True
        >>> engine.select_move(board)  # Input not modified
        <Move e2e4>
    """
    pass
```

**Contract Invariants**:
- **No Mutations**: Input `board` parameter is read-only. Engine must not call `board.push()` or `board.set_fen()` on the input.
- **Legal Move Guarantee**: Returned move must be in the set of legal moves for the position.
- **Determinism**: Same position + same engine state → same move (unless engine implements randomization explicitly).
- **Performance**: Evaluation must complete in <2 seconds for opening/middlegame positions.
- **Robustness**: Must return None (not raise exception) if position has no legal moves (shouldn't happen in normal game).

**Implementation Notes**:
- Safe lookahead pattern: Create copies with `board.copy()` for evaluation
- Never expose the input board to external code
- Thread safety: Single-threaded access assumed (no concurrent calls)

#### 2. `evaluate_position(board: chess.Board) → float`

**Purpose**: Evaluate the current board position from the perspective of the side to move.

**Signature**:
```python
@abstractmethod
def evaluate_position(self, board: chess.Board) -> float:
    """
    Evaluate position from current player's perspective.
    
    Contract (CRITICAL - Do not violate):
    - Input board MUST NOT be modified
    - Return value interpretation is consistent (see Scoring Convention below)
    - Larger scores mean better for current player
    - Return value should fit reasonable range [-1000, +1000] in typical positions
    
    Args:
        board (chess.Board): Position to evaluate
        
    Returns:
        float: Numeric score from current player's perspective
               Positive = current player advantage
               Zero = equal position
               Negative = current player disadvantage
               
    Examples:
        >>> board = chess.Board()
        >>> engine.evaluate_position(board)  # Starting position (should be ~0)
        0.0
        
        >>> # After white plays e2-e4 (small advantage)
        >>> board.push_san("e4")
        >>> board.push_san("e5")
        >>> engine.evaluate_position(board)
        25.0  # Positive because it's white's turn and white has advantage
    """
    pass
```

**Scoring Convention**:
```
Score Interpretation (in centipawns, typical range):
  +300: Moderate advantage
  +100: Small advantage
    +0: Equal position
   -100: Small disadvantage
   -300: Moderate disadvantage
  +999: Virtually winning
   -999: Virtually losing
```

**Contract Invariants**:
- **Read-Only**: Input board not modified
- **Sign Convention**: Positive = current-to-move advantage, negative = disadvantage
- **Range**: Should typically be in [-1000, +1000] unless position is clearly winning/losing
- **Consistency**: Same position always evaluates to same score (unless engine is non-deterministic by design)

**Implementation Notes**:
- Material balance is standard baseline (pawn=1, knight/bishop=3, rook=5, queen=9)
- Positional factors: piece placement, king safety, pawn structure
- Endgame: Prefer piece activity and pawn advancement

#### 3. `get_engine_name() → str`

**Purpose**: Return human-readable identifier for this engine.

**Signature**:
```python
def get_engine_name(self) -> str:
    """
    Return human-readable engine name.
    
    Returns:
        str: Engine name (e.g., "HeuristicEngine", "LLMEngine", "RandomEngine")
        
    Examples:
        >>> engine = HeuristicEngine()
        >>> engine.get_engine_name()
        "HeuristicEngine"
    """
    return self.__class__.__name__
```

**Default Implementation**: Returns `self.__class__.__name__` (usually sufficient).

---

## Compliance Checklist

### For Implementers (Checklist before merging)

- [ ] `select_move()` implemented (returns legal move or None)
- [ ] `select_move()` does NOT modify input board
- [ ] `evaluate_position()` implemented (returns float score)
- [ ] `evaluate_position()` does NOT modify input board
- [ ] All methods documented with docstrings
- [ ] Test coverage: At least 10 unit tests
  - [ ] Test move legality in 5+ positions
  - [ ] Test performance (<2 seconds)
  - [ ] Test evaluation consistency
  - [ ] Test edge cases (starting position, endgame)
  - [ ] Test no-legal-moves scenario
- [ ] Integration test with GameEngine
- [ ] Code review confirms no violations

### For Users (Runtime Checks)

```python
# Verify engine compliance
engine = MyEngine()
board = chess.Board()

# Check 1: select_move returns legal move
move = engine.select_move(board)
assert move is None or move in board.legal_moves, "Illegal move returned"

# Check 2: Board not mutated
original_fen = board.fen()
engine.select_move(board)
assert board.fen() == original_fen, "Engine mutated board"

# Check 3: evaluate_position returns number
score = engine.evaluate_position(board)
assert isinstance(score, (int, float)), "Evaluation not numeric"
```

---

## Example Implementations

### Example 1: Heuristic Engine (Reference Implementation)

```python
class HeuristicEngine(DecisionEngine):
    """Heuristic-based evaluation using minimax + alpha-beta pruning."""
    
    PIECE_VALUES = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }
    
    def select_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Minimax to depth 3 with alpha-beta pruning."""
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        best_move = legal_moves[0]
        best_score = float('-inf')
        
        for move in legal_moves:
            board_copy = board.copy()
            board_copy.push(move)
            score = self._minimax(board_copy, depth=3, is_maximizing=False)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def evaluate_position(self, board: chess.Board) -> float:
        """Material balance evaluation."""
        white_material = sum(
            len(board.pieces(piece, chess.WHITE)) * self.PIECE_VALUES[piece]
            for piece in chess.PIECE_TYPES
        )
        black_material = sum(
            len(board.pieces(piece, chess.BLACK)) * self.PIECE_VALUES[piece]
            for piece in chess.PIECE_TYPES
        )
        
        # Return from current player's perspective
        return (white_material - black_material) * 100 if board.turn else (black_material - white_material) * 100
```

### Example 2: Random Engine (for testing)

```python
import random

class RandomEngine(DecisionEngine):
    """Random legal move selection (for testing/baseline)."""
    
    def select_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Return random legal move."""
        legal_moves = list(board.legal_moves)
        return random.choice(legal_moves) if legal_moves else None
    
    def evaluate_position(self, board: chess.Board) -> float:
        """Return random score."""
        return random.uniform(-500, 500)
```

### Example 3: LLM Engine (Future - Stub)

```python
class LLMEngine(DecisionEngine):
    """LLM-based move selection using GPT-4 (future implementation)."""
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        # TODO: Initialize LLM client
    
    def select_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Prompt LLM for best move."""
        fen = board.fen()
        legal_moves = [board.san(move) for move in board.legal_moves]
        
        # TODO: Prompt LLM: "What's the best move in this position? FEN: [fen]"
        # TODO: Parse response to extract move
        # TODO: Validate move is legal
        
        return None  # Placeholder
    
    def evaluate_position(self, board: chess.Board) -> float:
        """Get LLM position assessment."""
        # TODO: Prompt LLM for evaluation
        return 0.0  # Placeholder
```

---

## Breaking Changes Policy

**Current Version**: 1.0.0

**Stability Guarantee**: This interface will NOT change in future versions unless absolutely necessary. Any changes will follow semantic versioning:
- **1.x.x** → 2.0.0: Breaking API changes
- **1.x.x** → 1.y.x: New optional methods added (default implementations provided)
- **1.x.x** → 1.x.z: Bug fixes, documentation updates

**Deprecation Path**: If changes are needed:
1. Announce deprecation with 1 release notice
2. Provide migration guide
3. Remove deprecated code in major version bump

---

## Testing Template

```python
# Copy to tests/unit/test_custom_engine.py

import pytest
import chess
from your_module import YourEngine

class TestYourEngine:
    """Compliance tests for custom engine."""
    
    @pytest.fixture
    def engine(self):
        return YourEngine()
    
    def test_select_move_returns_legal_move(self, engine):
        """Engine must return legal move or None."""
        board = chess.Board()
        move = engine.select_move(board)
        assert move is None or move in board.legal_moves
    
    def test_select_move_does_not_mutate_board(self, engine):
        """Engine must not modify input board."""
        board = chess.Board()
        original_fen = board.fen()
        engine.select_move(board)
        assert board.fen() == original_fen
    
    def test_evaluate_position_returns_number(self, engine):
        """Evaluation must return numeric score."""
        board = chess.Board()
        score = engine.evaluate_position(board)
        assert isinstance(score, (int, float))
    
    def test_performance_requirement(self, engine):
        """Engine must complete evaluation in under 2 seconds."""
        import time
        board = chess.Board()
        
        start = time.time()
        engine.select_move(board)
        elapsed = time.time() - start
        
        assert elapsed < 2.0, f"Too slow: {elapsed:.2f}s"
    
    def test_edge_case_no_legal_moves(self, engine):
        """Engine handles positions with no legal moves gracefully."""
        # Stalemate position
        board = chess.Board("7k/7P/7K/6B1/8/8/8/8 w - - 0 1")
        board.push_san("Bxh7")  # This puts black in stalemate
        
        move = engine.select_move(board)
        assert move is None
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-17 | Initial interface specification |

---

## Related Documents

- [Board Manager Interface](board-manager-interface.md)
- [Game Engine Interface](game-engine-interface.md)
- [Quickstart: Custom Engine](../quickstart.md#scenario-4-custom-engine-integration-future---llm)
