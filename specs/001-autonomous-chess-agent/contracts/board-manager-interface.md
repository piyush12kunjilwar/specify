# Contract: BoardManager Interface

**Status**: Stable (core interface for safe board state management)  
**Version**: 1.0.0  
**Location**: `chess_agent/board_manager.py`

---

## Purpose

Define the contract for safe board state management with immutability guarantees during lookahead evaluation. This interface provides:
- Encapsulated board state (never exposed directly)
- Safe move validation with python-chess correctness
- Immutable copies for lookahead evaluation
- Game history tracking for draw detection

---

## Interface Specification

### Class Definition

```python
class BoardManager:
    """Manages chess board state and move validation with immutability guarantees."""
```

### Constructor

#### `__init__(fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1") → None`

**Purpose**: Initialize board manager with optional FEN position.

**Signature**:
```python
def __init__(self, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
    """
    Initialize board manager with optional FEN position.
    
    Args:
        fen (str): Valid FEN string representing initial position
                   Defaults to standard starting position
                   
    Raises:
        ValueError: If FEN is invalid according to chess rules
        
    Examples:
        >>> board = BoardManager()  # Starting position
        >>> board = BoardManager("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")  # Custom
    """
```

**Contract Invariants**:
- FEN string is validated on initialization
- All subsequent operations maintain FEN validity
- No exceptions thrown for valid FEN

### Core Methods

#### 1. `get_board_copy() → chess.Board`

**Purpose**: Return immutable copy for safe lookahead evaluation.

**Signature**:
```python
def get_board_copy(self) -> chess.Board:
    """
    Return immutable copy of board for lookahead evaluation.
    
    Contract (CRITICAL):
    - Returned board is independent copy
    - Modifications to copy do NOT affect this manager's state
    - Safe for use in decision engine evaluation
    
    Returns:
        chess.Board: Independent copy of current position
        
    Examples:
        >>> board_mgr = BoardManager()
        >>> board_copy = board_mgr.get_board_copy()
        >>> board_copy.push_san("e4")  # Modifies copy only
        >>> board_mgr.get_fen() != board_copy.fen()  # Manager unchanged
        True
    """
```

**Contract Invariants**:
- Returned board is created via `chess.Board.copy()` (deep copy)
- Original board state never mutated by copy operations
- Thread-safe: Multiple threads can safely call this simultaneously (different copies created)

#### 2. `get_legal_moves() → List[chess.Move]`

**Purpose**: Get all legal moves from current position.

**Signature**:
```python
def get_legal_moves(self) -> List[chess.Move]:
    """
    Get all legal moves from current position.
    
    Contract:
    - List is complete and accurate per chess rules
    - Empty list only if game over (checkmate/stalemate)
    - Each move in list is legal (verified by python-chess)
    - List is immutable (caller cannot affect board by modifying list)
    
    Returns:
        List[chess.Move]: All legal moves for current player
        
    Examples:
        >>> board_mgr = BoardManager()
        >>> moves = board_mgr.get_legal_moves()
        >>> len(moves)  # Starting position has 20 legal moves
        20
        >>> moves[0] in board_mgr.get_legal_moves()  # Repeatable
        True
    """
```

**Contract Invariants**:
- List contains every legal move exactly once (no duplicates)
- List is ordered consistently across calls
- Caller can modify returned list without affecting board state
- Empty list only occurs in checkmate/stalemate (board.legal_moves is empty)

#### 3. `make_move(move: chess.Move) → bool`

**Purpose**: Apply move to board, updating history atomically.

**Signature**:
```python
def make_move(self, move: chess.Move) -> bool:
    """
    Apply move to board, updating history. Returns True if successful.
    
    Contract (CRITICAL - All-or-nothing):
    - If move is legal: Update board, history, return True
    - If move is illegal: No state changes, return False
    - Atomicity: Partial state updates NEVER occur
    - Move history always consistent with board state
    
    Args:
        move (chess.Move): Move to execute
        
    Returns:
        bool: True if move was legal and executed
              False if move was illegal (no state change)
              
    Raises:
        None (no exceptions; use return value to check success)
        
    Examples:
        >>> board_mgr = BoardManager()
        >>> move = chess.Move.from_uci("e2e4")
        >>> board_mgr.make_move(move)
        True
        >>> board_mgr.get_move_history()[-1] == move
        True
        
        >>> illegal = chess.Move.from_uci("e2e5")  # Pawn can't move 3 squares
        >>> board_mgr.make_move(illegal)
        False
        >>> len(board_mgr.get_move_history())  # Unchanged
        1
    """
```

**Contract Invariants**:
- **Atomicity**: Either entire move succeeds (board + history updated) or none of it does
- **Consistency**: After successful move, move appears in history and board reflects new position
- **Legality**: Move must be in `board.legal_moves` to succeed
- **No exceptions**: Invalid input returns False (doesn't raise)

#### 4. `validate_move(move: chess.Move) → bool`

**Purpose**: Check if move is legal without modifying board.

**Signature**:
```python
def validate_move(self, move: chess.Move) -> bool:
    """
    Check if move is legal without modifying board.
    
    Contract:
    - Read-only operation (no side effects)
    - Returns True IFF move is in legal_moves
    - Result is same as checking membership in get_legal_moves()
    
    Args:
        move (chess.Move): Move to validate
        
    Returns:
        bool: True if move is legal, False otherwise
        
    Examples:
        >>> board_mgr = BoardManager()
        >>> move = chess.Move.from_uci("e2e4")
        >>> board_mgr.validate_move(move)
        True
        
        >>> illegal = chess.Move.from_uci("e2e5")
        >>> board_mgr.validate_move(illegal)
        False
    """
```

**Contract Invariants**:
- No state modification (read-only)
- Result equivalent to: `move in board_mgr.get_legal_moves()`
- Repeatable: Multiple calls return same result

#### 5. `is_checkmate() → bool`

**Purpose**: Detect checkmate condition.

**Signature**:
```python
def is_checkmate() -> bool:
    """
    Detect checkmate condition.
    
    Contract:
    - Returns True IFF: King in check AND no legal moves
    - Exclusive with is_stalemate (never both True)
    
    Returns:
        bool: True if position is checkmate
        
    Examples:
        >>> # Fool's mate position
        >>> board_mgr = BoardManager()
        >>> board_mgr.make_move(chess.Move.from_uci("f2f3"))
        >>> board_mgr.make_move(chess.Move.from_uci("e7e5"))
        >>> board_mgr.make_move(chess.Move.from_uci("g2g4"))
        >>> board_mgr.make_move(chess.Move.from_uci("d8h4"))
        >>> board_mgr.is_checkmate()
        True
    """
```

**Contract Invariants**:
- Checkmate = (King in check) AND (no legal moves)
- Mutually exclusive with `is_stalemate()` (not both true)
- Determined by python-chess, guaranteed correct per chess rules

#### 6. `is_stalemate() → bool`

**Purpose**: Detect stalemate condition.

**Signature**:
```python
def is_stalemate() -> bool:
    """
    Detect stalemate condition.
    
    Contract:
    - Returns True IFF: King NOT in check AND no legal moves
    - Exclusive with is_checkmate (never both True)
    
    Returns:
        bool: True if position is stalemate (draw)
        
    Examples:
        >>> # Stalemate position
        >>> board_mgr = BoardManager()
        >>> board_mgr = BoardManager("7k/5K2/6B1/6B1/8/8/8/8 b - - 0 1")
        >>> board_mgr.is_stalemate()
        True
    """
```

**Contract Invariants**:
- Stalemate = (King NOT in check) AND (no legal moves)
- Mutually exclusive with `is_checkmate()` (not both true)
- Results in draw (1/2-1/2)

#### 7. `is_draw() → bool`

**Purpose**: Detect any draw condition.

**Signature**:
```python
def is_draw() -> bool:
    """
    Detect any draw condition:
    - Stalemate
    - Insufficient material
    - 50-move rule (or 75-move rule in python-chess)
    - Threefold repetition (or fivefold in python-chess)
    
    Contract:
    - Returns True if ANY draw condition is met
    - Includes all draw types per FIDE rules
    
    Returns:
        bool: True if position is drawn
        
    Examples:
        >>> board_mgr = BoardManager()
        >>> board_mgr = BoardManager("8/8/8/8/8/8/k1K5/8 w - - 0 1")  # K vs K (insufficient)
        >>> board_mgr.is_draw()
        True
    """
```

**Contract Invariants**:
- Covers all FIDE draw conditions
- python-chess uses 75-move rule (auto-draw) and fivefold repetition (auto-draw)
- May return True even if player hasn't claimed draw

#### 8. `get_fen() → str`

**Purpose**: Get current position as FEN string.

**Signature**:
```python
def get_fen() -> str:
    """
    Get current position as FEN string.
    
    Contract:
    - Returns valid FEN string per FIDE standard
    - Reconstructs exact position when passed to new BoardManager
    - Changes after each move
    
    Returns:
        str: FEN representation of current position
        
    Examples:
        >>> board_mgr = BoardManager()
        >>> fen = board_mgr.get_fen()
        >>> fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        True
        
        >>> board_mgr.make_move(chess.Move.from_uci("e2e4"))
        >>> board_mgr.get_fen() != fen  # FEN changed
        True
    """
```

**Contract Invariants**:
- Valid FIDE FEN format
- Describes exact current position
- Deterministic (same position → same FEN)

#### 9. `get_move_history() → List[chess.Move]`

**Purpose**: Return game history for analysis and draw detection.

**Signature**:
```python
def get_move_history() -> List[chess.Move]:
    """
    Return game history (all moves played).
    
    Contract:
    - Returns complete list of moves from start to current position
    - List is immutable (modifications don't affect board)
    - Moves are in order (move 1, move 2, ..., current)
    
    Returns:
        List[chess.Move]: All moves in game history
        
    Examples:
        >>> board_mgr = BoardManager()
        >>> board_mgr.make_move(chess.Move.from_uci("e2e4"))
        >>> board_mgr.make_move(chess.Move.from_uci("e7e5"))
        >>> history = board_mgr.get_move_history()
        >>> len(history)
        2
        >>> history[0].uci()
        "e2e4"
    """
```

**Contract Invariants**:
- Immutable copy (caller modifications don't affect board)
- Complete history from game start
- Moves in chronological order
- Consistent with current board state

#### 10. `get_san_move(move: chess.Move) → str`

**Purpose**: Convert move to standard algebraic notation.

**Signature**:
```python
def get_san_move(move: chess.Move) -> str:
    """
    Convert move to standard algebraic notation (SAN).
    
    Contract:
    - Returns valid SAN per FIDE standard
    - Same move produces same SAN in same position
    - Can be parsed with parse_move() to recover original move
    
    Args:
        move (chess.Move): Move to convert
        
    Returns:
        str: SAN representation (e.g., "e4", "Nf3", "O-O", "exd5=Q")
        
    Examples:
        >>> board_mgr = BoardManager()
        >>> move = chess.Move.from_uci("e2e4")
        >>> board_mgr.get_san_move(move)
        "e4"
        
        >>> # After e4 e5
        >>> move = chess.Move.from_uci("g1f3")
        >>> board_mgr.get_san_move(move)
        "Nf3"
    """
```

**Contract Invariants**:
- Valid SAN notation per FIDE
- Includes disambiguation if needed (e.g., "Nbd2")
- Includes check/checkmate notation (+, #) if applicable
- Deterministic (same move → same SAN)

#### 11. `parse_move(move_str: str) → Optional[chess.Move]`

**Purpose**: Parse move from algebraic notation or UCI format.

**Signature**:
```python
def parse_move(move_str: str) -> Optional[chess.Move]:
    """
    Parse move from algebraic notation (SAN) or UCI format.
    
    Contract:
    - Accepts both SAN ("e4", "Nf3", "O-O") and UCI ("e2e4") formats
    - Returns legal move if notation is valid in current position
    - Returns None if notation invalid or move is not legal
    - Tries SAN first, then UCI
    
    Args:
        move_str (str): Move in SAN or UCI notation
        
    Returns:
        Optional[chess.Move]: Parsed move if valid, None otherwise
        
    Examples:
        >>> board_mgr = BoardManager()
        >>> board_mgr.parse_move("e2e4")  # UCI
        Move.from_uci("e2e4")
        
        >>> board_mgr.parse_move("e4")  # SAN
        Move.from_uci("e2e4")
        
        >>> board_mgr.parse_move("invalid")  # Invalid
        None
    """
```

**Contract Invariants**:
- Accepts valid SAN and UCI notation
- Rejects invalid notation (returns None, no exception)
- Rejects illegal moves in current position (returns None)
- Deterministic parsing

#### 12. `reset() → None`

**Purpose**: Reset board to starting position.

**Signature**:
```python
def reset() -> None:
    """
    Reset board to starting position.
    
    Contract:
    - Clears all move history
    - Restores board to standard starting position
    - After reset, get_fen() returns standard starting FEN
    - All state reset atomically
    
    Examples:
        >>> board_mgr = BoardManager()
        >>> board_mgr.make_move(chess.Move.from_uci("e2e4"))
        >>> board_mgr.reset()
        >>> board_mgr.get_fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        True
        >>> board_mgr.get_move_history()
        []
    """
```

**Contract Invariants**:
- Atomic reset (all state cleared together)
- Returns to standard starting position
- Move history completely cleared

---

## Implementation Guarantees

### Immutability During Lookahead

```python
# GUARANTEED SAFE PATTERN:
def evaluate_position(board_mgr: BoardManager, engine: DecisionEngine) -> float:
    """Evaluate without mutating original board."""
    board_copy = board_mgr.get_board_copy()  # SAFE: Independent copy
    
    for move in board_copy.legal_moves:
        board_copy.push(move)
        score = engine.evaluate_position(board_copy)
        board_copy.pop()
    
    # board_mgr is GUARANTEED unchanged
    assert board_mgr.get_fen() == original_fen
```

### Legal Move Verification

```python
# ALL MOVES VALIDATED:
move = board_mgr.parse_move("e4")
if board_mgr.validate_move(move):
    if board_mgr.make_move(move):
        print(f"Move executed: {board_mgr.get_san_move(move)}")
    else:
        print("Move execution failed (shouldn't happen)")
else:
    print("Move is illegal")
```

---

## Edge Cases & Specifications

### Special Moves

| Move Type | SAN Format | Validation | Example |
|-----------|-----------|-----------|---------|
| Castling kingside | O-O | King/Rook unmoved, no pieces between, not in check | O-O |
| Castling queenside | O-O-O | King/Rook unmoved, no pieces between, not in check | O-O-O |
| En passant | exd5 (capture notation) | Pawn moved 2 squares previous turn | exd5 |
| Promotion | a8=Q (with piece) | Pawn reaches final rank | a7a8q or a8=Q |
| Check | e4+ | Move gives check | Nf6+ |
| Checkmate | Qe7# | Move gives checkmate | Qe7# |

### Draw Conditions

| Draw Type | Detection | Halfmove Clock | History |
|-----------|-----------|---|---------|
| Stalemate | King not in check + no legal moves | Not relevant | Not relevant |
| Insufficient material | K vs K, K+N vs K, K+B vs K | Not relevant | Not relevant |
| 50-move rule | 50 moves without capture or pawn move | ≥50 | Not used |
| Threefold repetition | Same position repeated 3 times | Not relevant | Used (FEN comparison) |

---

## Testing Template

```python
import pytest
import chess
from chess_agent import BoardManager

class TestBoardManager:
    """Compliance tests for BoardManager."""
    
    def test_initialization(self):
        """BoardManager initializes with valid FEN."""
        board = BoardManager()
        assert board.get_fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    
    def test_get_board_copy_is_independent(self):
        """Board copy is independent of original."""
        board = BoardManager()
        copy = board.get_board_copy()
        copy.push_san("e4")
        
        assert board.get_fen() != copy.fen()
    
    def test_make_move_atomicity(self):
        """Move execution is atomic (all or nothing)."""
        board = BoardManager()
        original_fen = board.get_fen()
        original_history = len(board.get_move_history())
        
        illegal = chess.Move.from_uci("e2e5")
        success = board.make_move(illegal)
        
        assert not success
        assert board.get_fen() == original_fen
        assert len(board.get_move_history()) == original_history
    
    def test_move_validation_consistency(self):
        """validate_move matches actual legality."""
        board = BoardManager()
        legal = chess.Move.from_uci("e2e4")
        
        assert board.validate_move(legal)
        assert board.make_move(legal)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-17 | Initial interface specification |

---

## Related Documents

- [Decision Engine Interface](decision-engine-interface.md)
- [Game Engine Interface](game-engine-interface.md)
- [Data Model](../data-model.md)
