# Data Model: Autonomous Chess Agent

**Date**: 2026-04-17  
**Phase**: Phase 1 - Design & Data Entities  
**Status**: Complete

---

## Core Entities

### 1. ChessBoard (Managed by BoardManager)

**Responsibility**: Encapsulate chess position state and move validation.

**Data Structure**:
```python
class BoardManager:
    _board: chess.Board          # Internal representation (bitboards)
    _move_history: List[Move]    # All moves played in game
    _position_history: List[str] # FEN snapshots for draw detection
```

**Key Attributes**:
| Attribute | Type | Source | Purpose |
|-----------|------|--------|---------|
| current_fen | str | python-chess board.fen() | Complete position snapshot |
| legal_moves | List[Move] | python-chess board.legal_moves | Enumeration of valid moves |
| is_check | bool | python-chess board.is_check() | King under attack flag |
| is_checkmate | bool | python-chess board.is_checkmate() | Game termination check |
| is_stalemate | bool | python-chess board.is_stalemate() | Draw condition check |
| is_insufficient_material | bool | python-chess | Draw condition check |
| castling_rights | str | FEN castling section | King/Rook movement flags |
| halfmove_clock | int | FEN halfmove counter | For 50-move rule |
| fullmove_number | int | FEN fullmove counter | Move numbering |

**Validation Rules**:
- All moves must be in legal_moves set
- Board state must remain consistent with FEN
- Move history must be traceable back to starting position
- Position history must include current position

**Invariants**:
- Legal moves generated only from valid board state
- En passant square only valid if legal pawn capture exists
- Castling rights revoked when king/rook moves
- Stalemate ≠ checkmate (different game termination)

---

### 2. Move

**Responsibility**: Represent a single chess action with complete information.

**Data Structure** (from python-chess):
```python
class Move:
    from_square: int      # 0-63 (a1=0, h8=63)
    to_square: int        # 0-63
    promotion: int        # Piece type (optional, for pawn promotions)
```

**Derived Attributes**:
| Attribute | Calculation | Example |
|-----------|-----------|---------|
| san | self._board.san(move) | "e4", "Nf3", "O-O", "exd5=Q" |
| uci | move.uci() | "e2e4", "a7a8q" |
| is_capture | move in board.legal_captures | True/False |
| is_check | board.is_check() after move | True/False |
| is_castling | board.is_castling(move) | True/False |
| is_en_passant | board.is_en_passant(move) | True/False |
| is_promotion | move.promotion is not None | True/False |

**Validation Rules**:
- Must be in current board's legal_moves set
- Promotion piece must be Knight, Bishop, Rook, or Queen (not Pawn/King)
- Source square must contain piece of moving player
- Destination square must be reachable by piece type
- Move must not expose king to check

---

### 3. GameState (Managed by GameEngine)

**Responsibility**: Orchestrate complete game lifecycle and turn management.

**Data Structure**:
```python
class GameEngine:
    _board: BoardManager              # Current position
    _engine: DecisionEngine           # Move selection strategy
    _game_over: bool                  # Game termination flag
    _result: Optional[str]            # '1-0', '0-1', '1/2-1/2'
    _move_count: int                  # Number of half-moves
```

**State Transitions**:
```
[STARTED] 
  ├→ human_move()
  │  └→ [HUMAN_MOVED]
  │     └→ agent_move()
  │        └→ [AGENT_MOVED] → (loop back if legal moves exist)
  └→ reset()
     └→ [STARTED]

[HUMAN_MOVED] or [AGENT_MOVED]
  ├→ is_checkmate() → [GAME_OVER_CHECKMATE]
  ├→ is_draw() → [GAME_OVER_DRAW]
  └→ continue game
```

**Game Result Values**:
| Result | Meaning | Termination |
|--------|---------|-------------|
| None | Game in progress | Active |
| "1-0" | White wins | Checkmate or opponent resignation |
| "0-1" | Black wins | Checkmate or opponent resignation |
| "1/2-1/2" | Draw | Stalemate, insufficient material, 50-move rule, threefold repetition |

**Invariants**:
- Exactly one player moves per turn (strict alternation)
- Turn determined by board.turn (True = white, False = black)
- Game termination conditions checked before next move
- Move count incremented atomically with board update

---

### 4. Agent (Programmatic Interface)

**Responsibility**: Provide stable Python API for game control.

**Data Structure**:
```python
class Agent:
    _board: BoardManager          # Game state container
    _engine: DecisionEngine       # Decision strategy
    _game: GameEngine             # Game controller
```

**Public Interface**:
| Method | Input | Output | Responsibility |
|--------|-------|--------|-----------------|
| make_move(move_str) | str: SAN/UCI notation | bool: success | Human move entry |
| get_agent_move() | None | str: SAN notation | Get AI move |
| get_board_state() | None | str: FEN | Position snapshot |
| get_legal_moves() | None | List[str]: SAN notation | Move enumeration |
| get_evaluation() | None | float: score | Position assessment |
| is_game_over() | None | bool | Game state query |
| get_result() | None | Optional[str] | Result query |
| reset() | None | None | Reset to starting |
| set_engine(engine) | DecisionEngine | None | Engine substitution |

**Contract Guarantees**:
- `make_move()` returns False if move illegal (no partial state updates)
- `get_agent_move()` returns None only if game over or no legal moves
- `get_legal_moves()` never empty unless game over
- `set_engine()` changes behavior for next `get_agent_move()` call
- No method mutates board except `make_move()` and `reset()`

---

### 5. Position (Snapshot for Analysis)

**Responsibility**: Immutable representation of board state at specific game moment.

**Data Structure**:
```python
class Position:
    fen: str                    # Complete position description
    move_number: int            # Full move count
    move_san: str              # Last move (SAN notation)
    evaluation: float          # Engine assessment at this position
```

**Usage**:
```python
# Generate position snapshots for analysis
game_positions = []
for move in game.get_move_history():
    pos = Position(
        fen=board.get_fen(),
        move_number=move_count,
        move_san=board.get_san_move(move),
        evaluation=engine.evaluate_position(board)
    )
    game_positions.append(pos)
```

---

## Entity Relationships

```
┌─────────────────────────────────────────────────────┐
│                      GameEngine                      │
│  (Orchestrates game flow, turn management)          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Uses:                                              │
│   ├── BoardManager (current position)               │
│   └── DecisionEngine (move selection)               │
│                                                      │
└─────────────────────────────────────────────────────┘
        ↓ (Managed by)                ↓ (Implements)
┌──────────────────────┐    ┌──────────────────────────┐
│   BoardManager       │    │   DecisionEngine (ABC)   │
│                      │    │                          │
│ - _board (chess)     │    │ + select_move()          │
│ - _move_history      │    │ + evaluate_position()    │
│ - _position_history  │    │                          │
└──────────────────────┘    └──────────────────────────┘
        ↓ (Contains)                  ↓ (Implemented by)
┌──────────────────────┐    ┌──────────────────────────┐
│   ChessBoard         │    │  HeuristicEngine         │
│ (python-chess.Board) │    │                          │
│                      │    │ - _piece_values          │
│ - position (FEN)     │    │ - _minimax()             │
│ - legal_moves        │    │ - _evaluate_position()   │
│ - castling_rights    │    │                          │
└──────────────────────┘    └──────────────────────────┘
        ↓ (Produces)
┌──────────────────────┐
│       Move           │
│                      │
│ - from_square        │
│ - to_square          │
│ - promotion          │
└──────────────────────┘
```

## State Transitions & Validation

### Move Execution Flow

```
Input: move_str (SAN/UCI)
  ↓
BoardManager.parse_move(move_str)
  ├→ Try SAN parsing (e.g., "e4", "Nf3", "O-O")
  └→ Fallback to UCI parsing (e.g., "e2e4")
  ↓ (Returns: chess.Move or None)
GameEngine.play_human_move()
  ├→ Validate move in legal_moves
  ├→ Update board state atomically
  ├→ Add to move history
  └→ Check game-over conditions
  ↓ (Returns: success boolean + message)
Output: Move executed or error returned
```

### Game Over Detection

```
After each move:
  1. Check: is_checkmate()?
     ├→ Yes: Result = winner's side, Game Over
     └→ No: Continue to step 2
  
  2. Check: is_draw()?
     ├→ Stalemate? → Result = "1/2-1/2"
     ├→ Insufficient material? → Result = "1/2-1/2"
     ├→ 50-move rule? → Result = "1/2-1/2"
     ├→ Threefold repetition? → Result = "1/2-1/2"
     └→ No: Continue to step 3
  
  3. Continue game, switch turns
```

---

## Edge Cases & Special Moves

### En Passant

**Data Representation**:
```
En passant square stored in FEN (e.g., "e3" means pawn captured on e3)
ChessBoard encapsulates: python-chess handles all validation
Move representation: Same as normal capture, python-chess validates
```

**Example**:
```
Position: White pawn on e4, Black pawn moves from f4 to f2 (illegal double-move)
Actually: Black pawn from f7 to f5 (two-square opening)
White can capture en passant: e4 × f5 (technically e4xf5)
python-chess validates: Move is in legal_moves only if en passant capture valid
```

### Castling

**Data Representation**:
```
Castling rights: FEN castling section (e.g., "KQkq" = all rights, "Kq" = some rights)
Move validation: King + Rook movement, no pieces in between, not in check
```

**Types**:
```
Kingside castling: e1-g1 (white) or e8-g8 (black), notation "O-O"
Queenside castling: e1-c1 (white) or e8-c8 (black), notation "O-O-O"
```

### Pawn Promotion

**Data Representation**:
```
Move.promotion field contains piece type (Knight=2, Bishop=3, Rook=4, Queen=5)
Example: a7a8q (white pawn to a8 promoting to queen)
```

**Validation**:
```
- Promotion only legal on 8th rank (white) or 1st rank (black)
- Promotion piece must be Knight, Bishop, Rook, or Queen
- Pawn must reach final rank via normal move or capture
```

---

## Data Persistence & Export

### FEN (Forsyth-Edwards Notation)

**Format**: `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`

**Components**:
```
1. Piece placement: (from white's perspective)
2. Active color: w or b
3. Castling availability: K (kingside), Q (queenside), k, q
4. En passant target square: square or '-'
5. Halfmove clock: moves since last capture/pawn move
6. Fullmove number: incremented after black's move
```

**Usage in this system**:
```python
# Save position
fen = board_manager.get_fen()

# Restore position
new_game = GameEngine(BoardManager(fen), engine)
```

### PGN (Portable Game Notation) - Future

**Structure**:
```
[Event "Chess Agent Game"]
[Date "2026.04.17"]
[White "Human"]
[Black "Agent"]
[Result "0-1"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 ... 32. Qe7# 0-1
```

---

## Validation & Integrity Constraints

### Board State Validation

| Constraint | Enforcer | Consequence of Violation |
|-----------|----------|--------------------------|
| One king per side, always present | python-chess | Invalid board state |
| Max 16 pieces per side | python-chess | N/A (not enforced, assumes valid FEN) |
| No pieces on same square | python-chess bitboards | Invalid position |
| Castling rights consistent with king/rook positions | FEN validation | Illegal castling |
| En passant only if legal pawn capture exists | python-chess | Invalid capture |
| Player to move not in check from previous move | Game invariant | Logic error |

### Move Validation

| Constraint | Enforcer | Consequence of Violation |
|-----------|----------|--------------------------|
| Move in legal_moves set | BoardManager.validate_move() | Rejected |
| Source square has piece of moving player | python-chess | Rejected |
| Destination reachable by piece type | python-chess | Rejected |
| Move doesn't expose king to check | python-chess | Rejected |
| Promotion piece valid (N/B/R/Q only) | python-chess | Rejected |

---

## Summary

The data model follows these principles:

1. **Encapsulation**: BoardManager wraps python-chess, hiding internal state
2. **Immutability**: Board copies used for lookahead, original never mutated
3. **Validation**: All constraints enforced at move execution time
4. **Traceability**: Move history maintained for draw detection and game analysis
5. **Extensibility**: DecisionEngine interface allows multiple evaluation strategies
6. **Simplicity**: Leverage python-chess for correctness, minimal custom logic

All entities and relationships align with constitutional principles of safe state management and decoupled architecture.
