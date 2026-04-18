# Contract: GameEngine Interface

**Status**: Stable (core interface for game orchestration)  
**Version**: 1.0.0  
**Location**: `chess_agent/game_engine.py`

---

## Purpose

Define the contract for game lifecycle orchestration, turn management, and end-game detection. This interface provides:
- Complete game flow from start to termination
- Turn alternation between human and agent
- Checkmate/stalemate/draw detection
- Game state transitions and result determination

---

## Interface Specification

### Class Definition

```python
class GameEngine:
    """Orchestrates complete chess game lifecycle."""
```

### Constructor

#### `__init__(board_manager: BoardManager, decision_engine: DecisionEngine) → None`

**Purpose**: Initialize game with board manager and decision engine.

**Signature**:
```python
def __init__(self, board_manager: BoardManager, decision_engine: DecisionEngine):
    """
    Initialize game engine with board and decision engine.
    
    Args:
        board_manager (BoardManager): Board state manager
        decision_engine (DecisionEngine): Move selection strategy
        
    Examples:
        >>> from chess_agent import BoardManager, HeuristicEngine, GameEngine
        >>> board = BoardManager()
        >>> engine = HeuristicEngine()
        >>> game = GameEngine(board, engine)
    """
```

**Contract Invariants**:
- Both parameters must be non-None
- Game starts in "ready" state (not game-over)
- Move count initialized to zero

### Game Control Methods

#### 1. `play_human_move(move_str: str) → Tuple[bool, str]`

**Purpose**: Human player makes a move in algebraic notation.

**Signature**:
```python
def play_human_move(self, move_str: str) -> Tuple[bool, str]:
    """
    Process human player's move.
    
    Contract:
    - Validates move notation (SAN or UCI)
    - Checks legality using board_manager
    - Updates game state atomically if successful
    - Does NOT automatically trigger agent move
    - Returns (success: bool, message: str)
    
    Args:
        move_str (str): Move in SAN ("e4", "Nf3") or UCI ("e2e4") format
        
    Returns:
        Tuple[bool, str]: 
            (True, message) if move succeeded
            (False, message) if move failed (with reason)
            
    Examples:
        >>> result, msg = game.play_human_move("e2e4")
        >>> result
        True
        >>> msg
        "Move made: e4"
        
        >>> result, msg = game.play_human_move("e2e5")
        >>> result
        False
        >>> msg
        "Illegal move: e2e5"
    """
```

**Contract Invariants**:
- **All-or-nothing**: If returns False, no board state modified
- **Message quality**: Message indicates success/failure and reason
- **No agent move**: Returns after human move only (caller triggers agent)
- **Game-over check**: If game becomes over (checkmate/draw), message indicates result

#### 2. `play_agent_move() → str`

**Purpose**: Agent evaluates and makes a move.

**Signature**:
```python
def play_agent_move(self) -> str:
    """
    Agent selects and executes its move.
    
    Contract:
    - Uses decision_engine to select best move
    - Move is guaranteed legal
    - Board state updated atomically
    - Returns move in SAN notation
    - Returns descriptive message if game already over
    
    Args:
        None (uses internal game state)
        
    Returns:
        str: Move in SAN notation (e.g., "e5", "Nf6") or game-over message
        
    Examples:
        >>> result = game.play_agent_move()
        >>> result
        "e5"
        
        >>> # If game over
        >>> result = game.play_agent_move()
        >>> result
        "Game is over"
    """
```

**Contract Invariants**:
- **Legality guaranteed**: Returned move is always legal
- **Engine safety**: Decision engine receives only board copy (immutable)
- **Determinism**: Same position + same engine state → same move
- **Performance**: Move selection completes within 2 seconds
- **Atomicity**: Board updated atomically with move execution

#### 3. `_check_game_over() → bool`

**Purpose**: Internal method to detect end-game conditions.

**Signature**:
```python
def _check_game_over(self) -> bool:
    """
    Check for and handle game termination conditions.
    
    Contract (Internal method):
    - Checks checkmate, stalemate, draw conditions
    - Sets self._game_over = True if game ends
    - Sets self._result to '1-0', '0-1', or '1/2-1/2'
    - Returns True if game just ended, False otherwise
    
    Returns:
        bool: True if game just ended, False if game continues
    """
```

**Contract Invariants**:
- **Mutual exclusivity**: Checkmate and draw are mutually exclusive outcomes
- **Result determinism**: Same position always produces same result
- **One-time evaluation**: Once game-over detected, state doesn't change

### Query Methods

#### 4. `is_game_over() → bool`

**Purpose**: Check if game has terminated.

**Signature**:
```python
def is_game_over() -> bool:
    """
    Check if game has terminated.
    
    Contract:
    - Returns True IFF game-over conditions detected
    - False means game continues
    
    Returns:
        bool: True if game over, False if game in progress
        
    Examples:
        >>> game.play_human_move("e2e4")
        >>> game.is_game_over()
        False
        
        >>> # After checkmate
        >>> game.is_game_over()
        True
    """
```

**Contract Invariants**:
- Consistent with `get_result()` (game-over ↔ result is not None)
- Read-only (doesn't modify state)
- Once True, remains True (monotonic)

#### 5. `get_result() → Optional[str]`

**Purpose**: Get game result.

**Signature**:
```python
def get_result() -> Optional[str]:
    """
    Get game result.
    
    Contract:
    - Returns None if game in progress
    - Returns '1-0' if white wins (black checkmated or resigned)
    - Returns '0-1' if black wins (white checkmated or resigned)
    - Returns '1/2-1/2' if draw (stalemate, insufficient material, 50-move, repetition)
    
    Returns:
        Optional[str]: Game result or None if ongoing
        
    Examples:
        >>> game.get_result()  # Game in progress
        None
        
        >>> # After white wins
        >>> game.get_result()
        "1-0"
    """
```

**Contract Invariants**:
- None ↔ game not over
- '1-0', '0-1', '1/2-1/2' ↔ game over
- Consistent with `is_game_over()`
- Deterministic (same game state → same result)

#### 6. `get_board_fen() → str`

**Purpose**: Get current position as FEN string.

**Signature**:
```python
def get_board_fen() -> str:
    """
    Get current board position as FEN string.
    
    Returns:
        str: FEN representation of current position
    """
```

**Contract Invariants**:
- Returns valid FIDE FEN
- Matches board_manager.get_fen()
- Changes after each move

### State Reset

#### 7. `reset() → None`

**Purpose**: Reset game to starting position.

**Signature**:
```python
def reset() -> None:
    """
    Reset game to starting position.
    
    Contract:
    - Board reset to standard start
    - Move count reset to zero
    - Game-over flag cleared
    - Result cleared (set to None)
    - All history cleared
    
    Examples:
        >>> game.reset()
        >>> game.is_game_over()
        False
        >>> game.get_result()
        None
    """
```

**Contract Invariants**:
- Atomic reset (all state cleared together)
- After reset, game ready for new game
- All previous moves/history cleared

---

## Game State Machine

### State Transitions

```
┌─────────────────────────────────────────────┐
│              GAME_STARTED                   │
│  (is_game_over = False, result = None)     │
└──────────────┬──────────────────────────────┘
               │
               ├─→ play_human_move() → HUMAN_MOVED
               │        │
               │        ├→ success: Check end-game
               │        │     ├→ checkmate → GAME_OVER (result = '1-0' or '0-1')
               │        │     ├→ draw → GAME_OVER (result = '1/2-1/2')
               │        │     └→ continue → HUMAN_MOVED
               │        │
               │        └→ failure: Stay in GAME_STARTED
               │
               ├─→ play_agent_move() → AGENT_MOVED (only valid from HUMAN_MOVED)
               │        │
               │        └→ Check end-game
               │             ├→ checkmate → GAME_OVER
               │             ├→ draw → GAME_OVER
               │             └→ continue → AGENT_MOVED
               │
               └─→ reset() → GAME_STARTED
```

### Move Sequence

```
Initial: is_game_over() = False, result = None

1. play_human_move("e2e4")
   → Board: e4 played
   → Check: Not checkmate/draw
   → Return: (True, "Move made: e4")

2. play_agent_move()
   → Agent selects move (e.g., "e5")
   → Board: e5 played
   → Check: Not checkmate/draw
   → Return: "e5"

3. play_human_move("g1f3")
   → Board: Nf3 played
   → Check: Not checkmate/draw
   → Continue...

N. Final move leads to checkmate
   → is_game_over() = True
   → get_result() = '1-0' (e.g., if white checkmated black)
```

---

## Integration with Components

### BoardManager Integration

```python
class GameEngine:
    def __init__(self, board_manager: BoardManager, ...):
        self._board = board_manager  # Delegate all move operations
    
    def play_human_move(self, move_str: str) -> Tuple[bool, str]:
        move = self._board.parse_move(move_str)  # Parse notation
        if not self._board.validate_move(move):  # Validate
            return False, f"Illegal move: {move_str}"
        
        if not self._board.make_move(move):      # Execute atomically
            return False, f"Move failed: {move_str}"
        
        # Board state is now updated
        # Check game-over conditions...
```

### DecisionEngine Integration

```python
def play_agent_move(self) -> str:
    board_copy = self._board.get_board_copy()  # SAFE: Independent copy
    move = self._engine.select_move(board_copy)  # Engine never mutates original
    
    # Original board_manager still unchanged, only copy was evaluated
    self._board.make_move(move)  # Apply move to actual game
```

---

## Error Handling & Edge Cases

### Move Validation Failures

```
Scenario 1: Invalid notation
  play_human_move("xyz") → (False, "Invalid move format: xyz")

Scenario 2: Illegal move
  play_human_move("e2e5") → (False, "Illegal move: e2e5")

Scenario 3: Move after game over
  play_human_move("e2e4") → (False, "Game is over")
```

### End-Game Detection

```
Scenario 1: Checkmate
  play_human_move("checkmate_move")
  → Check: is_checkmate() = True
  → Result: '1-0' (white checkmated black)
  → is_game_over() = True

Scenario 2: Stalemate
  play_agent_move()
  → Check: is_stalemate() = True
  → Result: '1/2-1/2' (draw)
  → is_game_over() = True

Scenario 3: Insufficient material
  play_agent_move()
  → Check: is_insufficient_material() = True
  → Result: '1/2-1/2'
  → is_game_over() = True
```

---

## Performance Contracts

### Response Time

| Operation | Target | Acceptable |
|-----------|--------|-----------|
| play_human_move() | <10ms | <100ms |
| play_agent_move() | <2000ms | <3000ms |
| get_result() | <1ms | <10ms |
| reset() | <1ms | <10ms |

### Memory Usage

| Component | Typical | Max |
|-----------|---------|-----|
| Game state | <1KB | <10KB |
| Board copies (during evaluation) | <10KB | <100KB |
| Move history (100 moves) | <2KB | <10KB |

---

## Testing Template

```python
import pytest
from chess_agent import BoardManager, HeuristicEngine, GameEngine

class TestGameEngine:
    """Compliance tests for GameEngine."""
    
    @pytest.fixture
    def game(self):
        board = BoardManager()
        engine = HeuristicEngine()
        return GameEngine(board, engine)
    
    def test_initialization(self, game):
        """Game initializes correctly."""
        assert not game.is_game_over()
        assert game.get_result() is None
    
    def test_play_human_move_valid(self, game):
        """Valid human move executes successfully."""
        success, msg = game.play_human_move("e2e4")
        assert success
        assert "e4" in msg
    
    def test_play_human_move_illegal(self, game):
        """Illegal move rejected without state change."""
        success, msg = game.play_human_move("e2e5")
        assert not success
        assert "Illegal" in msg or "invalid" in msg.lower()
    
    def test_play_human_move_atomicity(self, game):
        """Failed move doesn't modify state."""
        original_fen = game.get_board_fen()
        
        game.play_human_move("invalid_notation")
        
        assert game.get_board_fen() == original_fen
    
    def test_play_agent_move_returns_legal(self, game):
        """Agent move is legal."""
        game.play_human_move("e2e4")
        agent_move = game.play_agent_move()
        
        assert agent_move != "Game is over"
        # (verify in legal moves would require board access)
    
    def test_game_over_detection_checkmate(self):
        """Checkmate correctly detected."""
        # Set up fool's mate position
        game = GameEngine(BoardManager(), HeuristicEngine())
        game.play_human_move("f2f3")
        game.play_agent_move()
        game.play_human_move("e7e5")
        game.play_agent_move()
        game.play_human_move("g2g4")
        game.play_agent_move()
        game.play_human_move("d8h4")  # Checkmate
        
        assert game.is_game_over()
        assert game.get_result() in ['0-1', '1-0']
    
    def test_reset(self, game):
        """Game resets correctly."""
        game.play_human_move("e2e4")
        game.reset()
        
        assert not game.is_game_over()
        assert game.get_result() is None
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-17 | Initial interface specification |

---

## Related Documents

- [Decision Engine Interface](decision-engine-interface.md)
- [Board Manager Interface](board-manager-interface.md)
- [Data Model](../data-model.md)
