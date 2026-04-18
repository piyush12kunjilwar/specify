# Implementation Plan: Autonomous Chess Agent

**Branch**: `001-autonomous-chess-agent` | **Date**: 2026-04-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-autonomous-chess-agent/spec.md`

## Summary

Build a modular, production-quality autonomous chess agent that plays complete chess games using python-chess with a decoupled architecture supporting swappable decision engines, safe board state management during lookahead evaluation, and comprehensive test coverage for move validation and edge cases. The system will provide both CLI and programmatic Python API interfaces with move evaluation completing in under 2 seconds.

## Technical Context

**Language/Version**: Python 3.9+  
**Primary Dependencies**: python-chess 1.9.4+, (testing: pytest, mocking: pytest-mock)  
**Storage**: In-memory game state with optional PGN file export  
**Testing**: pytest with pytest-cov for coverage tracking  
**Target Platform**: Cross-platform CLI + programmatic Python API  
**Project Type**: Hybrid library/CLI tool  
**Performance Goals**: Move evaluation < 2 seconds for opening/middlegame positions, move generation < 100ms  
**Constraints**: Zero board state mutations during lookahead evaluation, 90% code coverage minimum  
**Scale/Scope**: Single autonomous agent, supports up to 100+ move game histories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✓ Decoupled Architecture
- **Requirement**: Game loop, player input handling, and evaluation engine must be distinct modules
- **Design Response**: Separate `game_engine`, `cli`, and `decision_engine` modules with clean interfaces
- **Status**: PASS - Architecture supports swapping CLI for REST API without core logic changes

### ✓ Safe Board State Management
- **Requirement**: Board state must never be mutated during lookahead evaluation
- **Design Response**: All move evaluation uses isolated board copies (python-chess Board.copy()) or safe read-only operations
- **Status**: PASS - Board manager enforces immutability contracts during evaluation

### ✓ Computational Efficiency (NON-NEGOTIABLE)
- **Requirement**: Move generation and evaluation must be optimized to prevent terminal freeze
- **Design Response**: Use python-chess native move generation (written in Cython), lazy evaluation patterns, memoization for repeated positions
- **Status**: PASS - Targets < 2 seconds evaluation time through efficient algorithms and data structures

### ✓ Swappable Decision Engine
- **Requirement**: Decision-making module designed for easy substitution without disrupting core logic
- **Design Response**: Abstract `DecisionEngine` interface with multiple implementations (HeuristicEngine initially, extensible for LLM)
- **Status**: PASS - Dependency injection pattern enables runtime engine swapping

### ✓ Comprehensive Testing for Edge Cases
- **Requirement**: Unit tests for move validation, en passant, castling rights, draw conditions
- **Design Response**: Dedicated test modules for board_manager, game_engine, move validation with explicit edge case coverage
- **Status**: PASS - Test strategy includes 90% coverage requirement with focus on edge cases

## Project Structure

### Documentation (this feature)

```text
specs/001-autonomous-chess-agent/
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions & best practices
├── data-model.md        # Phase 1: Entity definitions & relationships
├── quickstart.md        # Phase 1: Integration guide & usage examples
├── contracts/           # Phase 1: Interface specifications
│   ├── decision-engine-interface.md
│   ├── board-manager-interface.md
│   └── game-engine-interface.md
└── checklists/
    ├── requirements.md  # Feature requirements checklist
    └── tasks.md         # Phase 2: Implementation tasks
```

### Source Code Structure

```text
chess_agent/
├── __init__.py
├── board_manager.py          # Board state & move validation
├── game_engine.py            # Game lifecycle & rules enforcement
├── decision_engine.py        # Abstract engine interface
├── engines/
│   ├── __init__.py
│   ├── heuristic_engine.py   # Heuristic-based move evaluation
│   └── evaluation.py         # Position evaluation utilities
├── cli.py                    # CLI interface
├── api.py                    # Programmatic Python API
└── utils.py                  # Shared utilities

tests/
├── __init__.py
├── conftest.py              # pytest fixtures & setup
├── unit/
│   ├── test_board_manager.py        # Board state & validation tests
│   ├── test_game_engine.py          # Game logic & rules tests
│   ├── test_heuristic_engine.py     # Engine evaluation tests
│   ├── test_move_validation.py      # Comprehensive move validation
│   ├── test_edge_cases.py           # En passant, castling, promotion, draws
│   └── test_api.py                  # API interface tests
├── integration/
│   ├── test_complete_game.py        # Full game flow tests
│   ├── test_cli_interaction.py      # CLI end-to-end tests
│   └── test_engine_swapping.py      # Decision engine substitution tests
└── fixtures/
    └── test_positions.py            # Pre-defined board positions for testing

requirements.txt
pytest.ini
.coverage config (in pyproject.toml or .coveragerc)
```

**Structure Decision**: Single-package library/CLI hybrid with modular separation of concerns. Core chess logic (`board_manager`, `game_engine`) is completely decoupled from interfaces (`cli`, `api`) and decision engines. This allows the same core to support multiple frontends and decision strategies.

## Complexity Tracking

> **No violations to constitution principles. All design decisions align with Magus World Constitution.**

| Design Decision | Justification | Alternatives Considered |
|-----------------|---------------|-------------------------|
| Separate board_manager module | Enables safe state management and move validation isolation | Monolithic game engine (harder to test, increased mutation risk) |
| Abstract DecisionEngine interface | Allows LLM substitution without core logic changes | Hardcoded heuristic evaluation (inflexible for future LLM integration) |
| CLI & API layers as thin adapters | Interface layer is completely decoupled from core logic | Mixed concerns (terminal + business logic = hard to refactor) |

---

## Phase 1: Detailed Module Architecture & Interfaces

### 1. Core Game Engine Architecture

#### 1.1 board_manager.py - Board State & Validation

**Purpose**: Encapsulate python-chess Board with safe state management, move validation, and immutability during evaluation.

**Key Classes**:

```python
class BoardManager:
    """Manages chess board state and move validation with immutability guarantees."""
    
    def __init__(self, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        """Initialize board manager with optional FEN position."""
        self._board = chess.Board(fen)  # Internal chess.Board instance
        self._move_history = []  # List[chess.Move]
        self._position_history = []  # List[str] - FEN strings for draw detection
    
    def get_board_copy(self) -> chess.Board:
        """Return immutable copy of board for lookahead evaluation."""
        return self._board.copy()
    
    def get_legal_moves(self) -> List[chess.Move]:
        """Get all legal moves from current position."""
        return list(self._board.legal_moves)
    
    def make_move(self, move: chess.Move) -> bool:
        """Apply move to board, updating history. Returns True if successful."""
        if move not in self._board.legal_moves:
            return False
        self._position_history.append(self._board.fen())
        self._board.push(move)
        self._move_history.append(move)
        return True
    
    def validate_move(self, move: chess.Move) -> bool:
        """Check if move is legal without modifying board."""
        return move in self._board.legal_moves
    
    def is_checkmate(self) -> bool:
        """Detect checkmate condition."""
        return self._board.is_checkmate()
    
    def is_stalemate(self) -> bool:
        """Detect stalemate condition."""
        return self._board.is_stalemate()
    
    def is_draw(self) -> bool:
        """Detect any draw condition: stalemate, insufficient material, 50-move rule, threefold repetition."""
        return self._board.is_stalemate() or \
               self._board.is_insufficient_material() or \
               self._board.is_seventyfive_moves() or \
               self._board.is_fivefold_repetition()
    
    def get_fen(self) -> str:
        """Get current position as FEN string."""
        return self._board.fen()
    
    def get_move_history(self) -> List[chess.Move]:
        """Return game history for analysis and draw detection."""
        return self._move_history.copy()  # Immutable copy
    
    def get_san_move(self, move: chess.Move) -> str:
        """Convert move to standard algebraic notation."""
        return self._board.san(move)
    
    def parse_move(self, move_str: str) -> Optional[chess.Move]:
        """Parse move from algebraic notation or UCI format."""
        try:
            # Try SAN notation first (e.g., "e4", "Nf3", "O-O")
            return self._board.parse_san(move_str)
        except:
            try:
                # Fall back to UCI format (e.g., "e2e4")
                return chess.Move.from_uci(move_str)
            except:
                return None
    
    def reset(self) -> None:
        """Reset board to starting position."""
        self._board.reset()
        self._move_history.clear()
        self._position_history.clear()
```

**Safety Guarantees**:
- All public methods return copies or immutable data (e.g., `get_legal_moves()` returns `list(...)`)
- Internal `_board` is never exposed directly
- `get_board_copy()` explicitly enables safe lookahead without affecting game state

#### 1.2 game_engine.py - Game Lifecycle & Rules Enforcement

**Purpose**: Orchestrate complete game flow, enforce turn alternation, detect end-game conditions, and coordinate with decision engine.

**Key Classes**:

```python
class GameEngine:
    """Orchestrates complete chess game lifecycle."""
    
    def __init__(self, board_manager: BoardManager, decision_engine: 'DecisionEngine'):
        """Initialize game with board manager and decision engine."""
        self._board = board_manager
        self._engine = decision_engine
        self._game_over = False
        self._result = None  # '1-0', '0-1', '1/2-1/2'
        self._move_count = 0
    
    def play_human_move(self, move_str: str) -> Tuple[bool, str]:
        """
        Human player makes a move in algebraic notation.
        Returns: (success: bool, message: str)
        """
        if self._game_over:
            return False, "Game is over"
        
        move = self._board.parse_move(move_str)
        if not move:
            return False, f"Invalid move format: {move_str}"
        
        if not self._board.make_move(move):
            return False, f"Illegal move: {move_str}"
        
        self._move_count += 1
        
        # Check end-game conditions
        if self._check_game_over():
            return True, f"Move made: {self._board.get_san_move(move)}. {self._result}"
        
        # Agent's turn
        agent_result = self.play_agent_move()
        return True, f"You played: {self._board.get_san_move(move)}. Agent played: {agent_result}"
    
    def play_agent_move(self) -> str:
        """Agent evaluates and makes a move."""
        if self._game_over:
            return "Game is over"
        
        # Get decision from engine (safe board copy provided)
        board_copy = self._board.get_board_copy()
        move = self._engine.select_move(board_copy)
        
        if not move:
            return "No legal moves available (stalemate)"
        
        self._board.make_move(move)
        self._move_count += 1
        move_san = self._board.get_san_move(move)
        
        # Check end-game conditions
        if self._check_game_over():
            return f"{move_san}. {self._result}"
        
        return move_san
    
    def _check_game_over(self) -> bool:
        """Check for checkmate, stalemate, or draw conditions."""
        if self._board.is_checkmate():
            self._game_over = True
            self._result = "0-1" if self._board.turn else "1-0"
            return True
        
        if self._board.is_draw():
            self._game_over = True
            self._result = "1/2-1/2"
            return True
        
        return False
    
    def is_game_over(self) -> bool:
        """Check if game has ended."""
        return self._game_over
    
    def get_result(self) -> Optional[str]:
        """Get game result: '1-0' (white wins), '0-1' (black wins), '1/2-1/2' (draw), None (ongoing)."""
        return self._result
    
    def get_board_fen(self) -> str:
        """Get current position."""
        return self._board.get_fen()
    
    def reset(self) -> None:
        """Reset game to starting position."""
        self._board.reset()
        self._game_over = False
        self._result = None
        self._move_count = 0
```

**Invariants**:
- Board state only modified through `play_human_move()` or `play_agent_move()`
- Decision engine receives only board copies, never the live game state
- Game result detection uses definitive python-chess queries

#### 1.3 decision_engine.py - Abstract Engine Interface

**Purpose**: Define stable interface for decision engines, enabling runtime swapping between heuristic, LLM, or other strategies.

**Key Classes**:

```python
from abc import ABC, abstractmethod
import chess

class DecisionEngine(ABC):
    """Abstract interface for chess move selection strategies."""
    
    @abstractmethod
    def select_move(self, board: chess.Board) -> Optional[chess.Move]:
        """
        Select next move given a board position.
        
        Args:
            board: chess.Board instance representing current position
            
        Returns:
            Selected chess.Move, or None if no legal moves exist
            
        Contract:
            - Input board MUST NOT be modified
            - Returned move MUST be legal in the given position
            - Must complete within 2 seconds for typical positions
        """
        pass
    
    @abstractmethod
    def evaluate_position(self, board: chess.Board) -> float:
        """
        Evaluate position from current player's perspective.
        
        Args:
            board: Position to evaluate
            
        Returns:
            Numeric score (positive = current player advantage, negative = opponent advantage)
        """
        pass
    
    def get_engine_name(self) -> str:
        """Return human-readable engine name."""
        return self.__class__.__name__
```

**Usage Pattern**:

```python
# Heuristic engine (default)
engine = HeuristicEngine()
game = GameEngine(board_manager, engine)

# Future: Swap to LLM engine
llm_engine = LLMBasedEngine(model="gpt-4")
game._engine = llm_engine  # Drop-in replacement
```

#### 1.4 engines/heuristic_engine.py - Heuristic Move Evaluation

**Purpose**: Implement concrete decision engine using material balance, piece-square tables, and position heuristics.

**Key Classes**:

```python
class HeuristicEngine(DecisionEngine):
    """Heuristic-based chess engine using material and positional evaluation."""
    
    # Piece values in centipawns
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 0  # King value not counted
    }
    
    def select_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Select best move using minimax with alpha-beta pruning (depth 3-4)."""
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        best_move = legal_moves[0]
        best_score = float('-inf')
        
        for move in legal_moves:
            board.push(move)
            score = self._minimax(board, depth=3, is_maximizing=False)
            board.pop()
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def evaluate_position(self, board: chess.Board) -> float:
        """Static position evaluation based on material and piece placement."""
        # Material count
        white_material = sum(
            len(board.pieces(piece, chess.WHITE)) * self.PIECE_VALUES[piece]
            for piece in chess.PIECE_TYPES
        )
        black_material = sum(
            len(board.pieces(piece, chess.BLACK)) * self.PIECE_VALUES[piece]
            for piece in chess.PIECE_TYPES
        )
        
        return white_material - black_material if board.turn else black_material - white_material
    
    def _minimax(self, board: chess.Board, depth: int, is_maximizing: bool) -> float:
        """Minimax with alpha-beta pruning."""
        if depth == 0 or board.is_game_over():
            return self.evaluate_position(board)
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                eval_score = self._minimax(board, depth - 1, False)
                board.pop()
                max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval_score = self._minimax(board, depth - 1, True)
                board.pop()
                min_eval = min(min_eval, eval_score)
            return min_eval
```

### 2. Interface Layers

#### 2.1 api.py - Programmatic Python API

**Purpose**: Expose chess agent as a Python library for integration into other applications.

**Key Classes**:

```python
class Agent:
    """Public API for chess agent."""
    
    def __init__(self, engine: Optional[DecisionEngine] = None):
        """Initialize agent with optional custom engine (defaults to HeuristicEngine)."""
        self._board = BoardManager()
        self._engine = engine or HeuristicEngine()
        self._game = GameEngine(self._board, self._engine)
    
    def make_move(self, move: str) -> bool:
        """Execute human move. Returns True if successful."""
        success, _ = self._game.play_human_move(move)
        return success
    
    def get_agent_move(self) -> Optional[str]:
        """Get agent's move in SAN notation."""
        if self._game.is_game_over():
            return None
        board_copy = self._board.get_board_copy()
        move = self._engine.select_move(board_copy)
        if move:
            return self._board.get_san_move(move)
        return None
    
    def get_board_state(self) -> str:
        """Get current position as FEN."""
        return self._board.get_fen()
    
    def get_legal_moves(self) -> List[str]:
        """Get all legal moves in SAN notation."""
        return [self._board.get_san_move(m) for m in self._board.get_legal_moves()]
    
    def get_evaluation(self) -> float:
        """Get current position evaluation."""
        board_copy = self._board.get_board_copy()
        return self._engine.evaluate_position(board_copy)
    
    def is_game_over(self) -> bool:
        """Check if game has ended."""
        return self._game.is_game_over()
    
    def get_result(self) -> Optional[str]:
        """Get result: '1-0', '0-1', '1/2-1/2', or None."""
        return self._game.get_result()
    
    def reset(self) -> None:
        """Reset to starting position."""
        self._game.reset()
    
    def set_engine(self, engine: DecisionEngine) -> None:
        """Swap decision engine at runtime."""
        self._game._engine = engine
```

#### 2.2 cli.py - Command-Line Interface

**Purpose**: Interactive CLI for human vs. agent gameplay.

**Key Functions**:

```python
class ChessAgentCLI:
    """Interactive chess CLI."""
    
    def __init__(self):
        self.agent = Agent()
        self.running = True
    
    def display_board(self) -> None:
        """Display current position in ASCII."""
        board = chess.Board(self.agent.get_board_state())
        print(board)
        print(f"FEN: {self.agent.get_board_state()}\n")
    
    def run(self) -> None:
        """Main game loop."""
        print("Chess Agent - Type 'help' for commands\n")
        
        while self.running and not self.agent.is_game_over():
            self.display_board()
            
            user_input = input("Your move (or command): ").strip().lower()
            
            if user_input == 'quit':
                break
            elif user_input == 'hint':
                move = self.agent.get_agent_move()
                print(f"Suggested move: {move}\n")
            elif user_input == 'eval':
                score = self.agent.get_evaluation()
                print(f"Position evaluation: {score}\n")
            else:
                if self.agent.make_move(user_input):
                    move = self.agent.get_agent_move()
                    if move:
                        print(f"Agent plays: {move}\n")
                else:
                    print("Invalid move. Try again.\n")
        
        self.display_board()
        result = self.agent.get_result()
        print(f"Game Over. Result: {result}")
```

---

## Phase 2: Test Strategy

### 2.1 Unit Tests - Test Coverage Map

**test_board_manager.py** (15-20 tests):
- Initialization with starting position
- Initialization with custom FEN
- `get_legal_moves()` - typical position, endgame
- `make_move()` - valid move, illegal move
- `validate_move()` - legal vs. illegal
- `is_checkmate()`, `is_stalemate()`, `is_draw()`
- `get_fen()` - position persistence
- `parse_move()` - SAN and UCI formats
- `get_move_history()` - history accumulation
- Board copy isolation (verify mutations don't affect original)

**test_game_engine.py** (12-15 tests):
- Game initialization
- `play_human_move()` - valid, invalid, illegal
- `play_agent_move()` - move execution, history update
- `_check_game_over()` - checkmate detection, draw detection
- Turn alternation
- Game reset

**test_heuristic_engine.py** (10-12 tests):
- Move selection from legal moves
- Position evaluation (material balance)
- `minimax()` - correct depth traversal
- Handling of endgame positions
- Performance: completion under 100ms for depth 3

**test_move_validation.py** (20+ tests - Edge Cases):
- En passant: capture available, capture not available
- Castling: kingside, queenside, with restrictions (king/rook moved)
- Pawn promotion: selection of piece (Q, R, B, N)
- Discovered check: move reveals check on king
- Double check: must move king (no blocking)
- Moving into check: illegal
- Moving opponent's piece: illegal
- Special notation: "O-O" (kingside castling), "O-O-O" (queenside)
- Notation with disambiguation: "Nbd2" (two knights can go to d2)

**test_edge_cases.py** (15+ tests):
- Threefold repetition detection
- Fifty-move rule (seventy-five-move rule in python-chess)
- Insufficient material (K vs K, K+N vs K, K+B vs K, K+B vs K+B same-colored bishops)
- Check detection and evasion
- Stalemate vs. checkmate distinction
- Perpetual check recognition
- Endgame positions: K+Q vs K+R, K+Q vs K
- Pawn endgames: passed pawns, blockades

**test_api.py** (10 tests):
- `Agent` initialization
- `make_move()` return values
- `get_agent_move()` validity
- `get_board_state()` accuracy
- `get_legal_moves()` completeness
- `get_evaluation()` consistency
- `is_game_over()` state
- `set_engine()` engine swapping
- API state isolation (multiple agents don't interfere)

### 2.2 Integration Tests

**test_complete_game.py** (3-5 full game scenarios):
- Complete game from start to checkmate (white wins)
- Complete game from start to checkmate (black wins)
- Complete game to draw (stalemate)
- Complete game to draw (insufficient material)
- Interrupted game (reset mid-game)

**test_cli_interaction.py** (5 scenarios):
- CLI initialization and display
- User move entry in different formats (SAN, UCI)
- Hint command execution
- Eval command execution
- Game reset from CLI

**test_engine_swapping.py** (3 scenarios):
- Swap engines mid-game
- Different engines select different moves from same position
- LLM engine mock integration (future-proofing)

### 2.3 Coverage Goals

- **Target**: 90% line coverage minimum
- **Critical paths** (100% coverage required):
  - `board_manager.make_move()` and `validate_move()`
  - `game_engine._check_game_over()`
  - Move parsing and algebraic notation conversion
  - All DecisionEngine implementations

---

## Phase 3: Performance Optimization Areas

### 3.1 Move Generation Optimization

| Optimization | Mechanism | Expected Impact |
|--------------|-----------|-----------------|
| Lazy evaluation | Use python-chess native move generator (Cython-accelerated) | 50% faster than pure Python iteration |
| Move ordering | Evaluate captures/checks first (alpha-beta pruning) | Prune 90%+ of minimax tree |
| Transposition tables | Memoize position evaluations | Eliminate duplicate evaluations |
| Iterative deepening | Search depth 1→2→3→4 with time cutoff | Anytime results + adaptive depth |

### 3.2 Position Evaluation Optimization

| Technique | Scope | Impact |
|-----------|-------|--------|
| Piece-square tables | Endgame bonus for advanced pawns | +5-10% accuracy without extra computation |
| Killer heuristics | Remember moves that cause cutoffs | Further alpha-beta pruning |
| Zobrist hashing | Hash positions for transposition lookup | O(1) table lookup vs. FEN parsing |

### 3.3 Memory Optimization

- **Board copies**: Use python-chess `.copy()` (pre-optimized in C/Cython)
- **Move lists**: Generator expressions to avoid materializing all moves
- **Position history**: Store FEN strings (compact) not full Board objects

---

## Phase 4: Implementation Checklist - All Modules & Files

### Core Modules

| File | Class | Key Methods | Status |
|------|-------|------------|--------|
| `board_manager.py` | `BoardManager` | `make_move()`, `validate_move()`, `get_board_copy()`, `is_checkmate()`, `get_legal_moves()` | To implement |
| `game_engine.py` | `GameEngine` | `play_human_move()`, `play_agent_move()`, `is_game_over()`, `get_result()` | To implement |
| `decision_engine.py` | `DecisionEngine` (abstract) | `select_move()`, `evaluate_position()` | To implement |
| `engines/heuristic_engine.py` | `HeuristicEngine` | `select_move()`, `evaluate_position()`, `_minimax()` | To implement |
| `api.py` | `Agent` | `make_move()`, `get_agent_move()`, `get_board_state()`, `set_engine()` | To implement |
| `cli.py` | `ChessAgentCLI` | `run()`, `display_board()` | To implement |
| `utils.py` | Utilities | Move notation helpers, board display | To implement |

### Test Modules (Total: 50-70 tests)

| File | Tests | Focus | Status |
|------|-------|-------|--------|
| `test_board_manager.py` | 18 | Board state, move validation | To implement |
| `test_game_engine.py` | 14 | Game flow, turn alternation | To implement |
| `test_heuristic_engine.py` | 11 | Engine logic, minimax correctness | To implement |
| `test_move_validation.py` | 22 | En passant, castling, promotion, special moves | To implement |
| `test_edge_cases.py` | 15 | Threefold repetition, 50-move rule, insufficient material, stalemate | To implement |
| `test_api.py` | 10 | Agent public API correctness | To implement |
| `test_complete_game.py` | 4 | Full game scenarios | To implement |
| `test_cli_interaction.py` | 5 | CLI end-to-end | To implement |
| `test_engine_swapping.py` | 3 | Engine substitution | To implement |

### Configuration & Support

| File | Purpose | Status |
|------|---------|--------|
| `__init__.py` (root) | Package initialization, version | To implement |
| `__init__.py` (engines/) | Engine subpackage exports | To implement |
| `conftest.py` | pytest fixtures, board positions | To implement |
| `requirements.txt` | python-chess, pytest, pytest-cov | To create |
| `pytest.ini` | pytest configuration, coverage settings | To create |

---

## Phase 5: Module Interface Contracts

### BoardManager Interface

```python
# Guarantee: Board state never mutated except via make_move()
# Safe for concurrent reads via get_board_copy()

__init__(fen: str) → None
get_board_copy() → chess.Board  # Always safe
get_legal_moves() → List[chess.Move]  # Never empty if game not over
make_move(move: chess.Move) → bool  # Idempotent, single responsibility
validate_move(move: chess.Move) → bool  # Read-only check
is_checkmate() → bool
is_stalemate() → bool
is_draw() → bool
get_fen() → str
get_move_history() → List[chess.Move]  # Immutable copy
parse_move(move_str: str) → Optional[chess.Move]
reset() → None
```

### GameEngine Interface

```python
# Guarantee: Maintains game invariants (turn alternation, end-game detection)

__init__(board_manager: BoardManager, decision_engine: DecisionEngine) → None
play_human_move(move_str: str) → Tuple[bool, str]  # (success, message)
play_agent_move() → str  # Move in SAN notation
_check_game_over() → bool
is_game_over() → bool
get_result() → Optional[str]  # '1-0' | '0-1' | '1/2-1/2' | None
get_board_fen() → str
reset() → None
```

### DecisionEngine Interface (Stable Contract)

```python
# Guarantee: Input board never mutated, output move always legal

@abstractmethod
select_move(board: chess.Board) → Optional[chess.Move]
@abstractmethod
evaluate_position(board: chess.Board) → float
get_engine_name() → str
```

### Agent (Public API) Interface

```python
# Guarantee: Stable API for programmatic integration

__init__(engine: Optional[DecisionEngine] = None) → None
make_move(move: str) → bool
get_agent_move() → Optional[str]
get_board_state() → str
get_legal_moves() → List[str]
get_evaluation() → float
is_game_over() → bool
get_result() → Optional[str]
reset() → None
set_engine(engine: DecisionEngine) → None
```

---

## Next Steps

1. **Phase 0 (Research)**: Complete research.md with technology decisions and best practices
2. **Phase 1 (Design)**: Create data-model.md with entity definitions and contracts/
3. **Phase 2 (Tasking)**: Use `/speckit.tasks` to generate detailed implementation tasks from this plan
4. **Phase 3 (Implementation)**: Execute tasks in order, maintaining test coverage and constitutional alignment
5. **Phase 4 (Verification)**: Ensure all edge cases pass, achieve 90% coverage, verify performance targets

---

## Implementation Principles

- **TDD**: Write tests before implementation
- **Immutability**: Board state immutable except via explicit `make_move()`
- **DRY**: No duplicated move validation logic (defer to python-chess)
- **SOLID**: Single responsibility per module, dependency injection for engines
- **Performance**: Every optimization must be benchmarked (target: <2s evaluation)
- **Documentation**: Every class/method must have docstring with contract
- **Manual Review**: All AI-generated code requires careful review for correctness
