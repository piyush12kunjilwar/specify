# Tasks: Autonomous Chess Agent

**Input**: Design documents from `/specs/001-autonomous-chess-agent/`  
**Branch**: `001-autonomous-chess-agent`  
**Approach**: Test-Driven Development (TDD) - tests written first, fail initially, then implementation  
**Tests**: Comprehensive unit tests + integration tests (required per user request)  
**Organization**: Tasks grouped by user story with module dependency ordering  

**Format**: `[ID] [P?] [Story?] [⏱️ Effort] Description — Success Criteria`

- **[P]**: Can run in parallel (different files, independent modules)
- **[Story]**: Which user story (US1, US2, US3, US4)
- **[⏱️ Effort]**: Time estimate (30m, 1h, 2h, 4h, 1d)
- Include exact file paths

---

## Phase 1: Setup & Project Initialization

**Purpose**: Create project structure, install dependencies, configure tooling  
**Target**: Ready for TDD implementation

### Environment & Dependencies

- [ ] T001 ⏱️ 30m Create project directory structure per plan.md at chess_agent/ root
  - Create directories: `chess_agent/`, `chess_agent/engines/`, `tests/`, `tests/unit/`, `tests/integration/`, `tests/fixtures/`
  - Success: All directories exist with `__init__.py` files created

- [ ] T002 ⏱️ 30m Create requirements.txt with project dependencies
  - Location: `requirements.txt` (project root)
  - Dependencies: `python-chess==1.9.4`, `pytest>=7.0`, `pytest-cov>=3.0`, `pytest-mock>=3.6`
  - Success: File created, all packages listed with versions

- [ ] T003 [P] ⏱️ 20m Create pytest.ini configuration file
  - Location: `pytest.ini` (project root)
  - Config: testpaths=tests, python_files=test_*.py, addopts=--cov=chess_agent --cov-report=html --cov-report=term-missing
  - Success: pytest can discover and run tests with coverage

- [ ] T004 [P] ⏱️ 20m Create pyproject.toml with project metadata
  - Location: `pyproject.toml` (project root)
  - Include: package name, version, author, description, python_requires>=3.9
  - Success: Poetry/setuptools can read configuration

- [ ] T005 [P] ⏱️ 20m Create .gitignore and .coveragerc files
  - .gitignore: __pycache__/, *.pyc, .coverage, htmlcov/, .pytest_cache/, dist/, build/
  - .coveragerc: omit=tests/*, include=chess_agent/*
  - Success: Coverage reports and build artifacts properly ignored

---

## Phase 2: Foundational - Core Interfaces & Base Classes

**Purpose**: Define abstract contracts and base interfaces  
**⚠️ CRITICAL**: These must be complete before user story implementation  
**Note**: No tests in this phase (abstract interfaces are tested via implementations)

### Abstract Interfaces

- [ ] T006 ⏱️ 45m Create DecisionEngine abstract interface
  - Location: `chess_agent/decision_engine.py`
  - Classes: `DecisionEngine` (abstract base class)
  - Methods: `select_move(board: chess.Board) → Optional[chess.Move]` (abstract), `evaluate_position(board: chess.Board) → float` (abstract), `get_engine_name() → str` (concrete)
  - Success: Interface defined per contract, no implementation (only raise NotImplementedError)
  - Code Review Checkpoint: Verify abstract methods are pure contracts

- [ ] T007 [P] ⏱️ 30m Create __init__.py package files with exports
  - Locations: `chess_agent/__init__.py`, `chess_agent/engines/__init__.py`, `tests/__init__.py`
  - Exports: Agent, BoardManager, GameEngine, DecisionEngine, HeuristicEngine
  - Success: All public classes importable from package root

- [ ] T008 [P] ⏱️ 20m Create conftest.py with pytest fixtures
  - Location: `tests/conftest.py`
  - Fixtures: `starting_board()` → FEN string of starting position, `sample_positions()` → dict of test positions
  - Success: Fixtures available in all test modules without import

---

## Phase 3: User Story 1 - Play Complete Chess Game (Priority: P1) 🎯 MVP

**Goal**: Build core game engine with board state management and move validation  
**Independent Test**: Launch game, play valid moves, verify board state updates, detect checkmate/draws correctly  
**Parallel Opportunities**: T009-T011 can run in parallel, T012-T013 can run in parallel  

### Unit Tests for BoardManager (TDD - Write First)

- [ ] T009 ⏱️ 1h [US1] Create unit test suite for board_manager.py
  - Location: `tests/unit/test_board_manager.py`
  - Tests (must FAIL before implementation):
    * `test_init_default_position`: Verify starting FEN
    * `test_init_custom_fen`: Initialize with custom position
    * `test_get_board_copy_isolation`: Copy modifications don't affect original (critical!)
    * `test_get_legal_moves_starting_position`: Returns 20 moves
    * `test_get_legal_moves_empty_list_checkmate`: Empty when checkmate
    * `test_make_move_valid`: Board state updates, move added to history
    * `test_make_move_invalid`: Returns False, no state change
    * `test_validate_move_legal`: Returns True for legal move
    * `test_validate_move_illegal`: Returns False for illegal move
    * `test_is_checkmate`: Detects checkmate correctly
    * `test_is_stalemate`: Detects stalemate correctly
    * `test_is_draw`: Detects insufficient material, 50-move rule
    * `test_get_fen`: Returns current position FEN
    * `test_parse_move_san_notation`: "e4" → chess.Move
    * `test_parse_move_uci_notation`: "e2e4" → chess.Move
    * `test_parse_move_castling`: "O-O", "O-O-O" → correct moves
    * `test_parse_move_invalid`: Returns None
    * `test_get_move_history_isolation`: History immutable to caller
    * `test_reset`: Board returns to starting position, history cleared
  - Success: All 18 tests present, all FAIL initially

- [ ] T010 [P] ⏱️ 1h [US1] Create unit test suite for move validation edge cases
  - Location: `tests/unit/test_move_validation.py`
  - Tests (must FAIL before implementation):
    * `test_en_passant_capture_available`: En passant capture succeeds
    * `test_en_passant_capture_not_available`: En passant not available when pawn didn't just move 2 squares
    * `test_castling_kingside_white`: White kingside castling succeeds
    * `test_castling_queenside_black`: Black queenside castling succeeds
    * `test_castling_blocked_by_piece`: Castling fails if path blocked
    * `test_castling_king_moved`: Castling unavailable after king moves
    * `test_castling_rook_moved`: Castling unavailable after rook moves
    * `test_pawn_promotion_queen`: Pawn promotes to queen
    * `test_pawn_promotion_knight`: Pawn promotes to knight
    * `test_pawn_promotion_rook`: Pawn promotes to rook
    * `test_pawn_promotion_bishop`: Pawn promotes to bishop
    * `test_illegal_promotion_pawn`: Cannot promote to pawn
    * `test_discovered_check_illegal`: Move exposing king to check fails
    * `test_moving_into_check_illegal`: Cannot move king into check
    * `test_moving_opponent_piece_illegal`: Cannot move opponent's piece
    * `test_double_check_must_move_king`: When in double check, only king move valid
    * `test_blocked_check_possible`: Can block single check
    * `test_threefold_repetition_detection`: Detects same position 3 times
    * `test_fifty_move_rule`: Detects 50 moves without capture/pawn move
    * `test_insufficient_material_k_vs_k`: King vs King is draw
    * `test_insufficient_material_k_n_vs_k`: King+Knight vs King is draw
    * `test_insufficient_material_k_b_vs_k`: King+Bishop vs King is draw
  - Success: All 22 tests present, all FAIL initially

- [ ] T011 [P] ⏱️ 1h [US1] Create unit test suite for game_engine.py
  - Location: `tests/unit/test_game_engine.py`
  - Tests (must FAIL before implementation):
    * `test_game_init`: GameEngine initializes with board and engine
    * `test_play_human_move_valid`: Valid move succeeds, returns (True, message)
    * `test_play_human_move_invalid_format`: Invalid format returns (False, message)
    * `test_play_human_move_illegal`: Illegal move returns (False, message)
    * `test_play_human_move_updates_board`: Board state changes after valid move
    * `test_play_agent_move`: Agent evaluates and selects move
    * `test_play_agent_move_updates_board`: Board state changes after agent move
    * `test_game_alternation_white_then_black`: White moves, then black moves
    * `test_game_alternation_black_then_white`: Black moves after white
    * `test_checkmate_detection_white`: Detects white checkmated (result='0-1')
    * `test_checkmate_detection_black`: Detects black checkmated (result='1-0')
    * `test_stalemate_detection`: Detects stalemate (result='1/2-1/2')
    * `test_game_over_stops_further_moves`: Can't play after game ends
    * `test_is_game_over(): Returns False at start, True at end
    * `test_get_result_none_ongoing`: Returns None during game
    * `test_get_result_checkmate`: Returns correct result
    * `test_reset_clears_state`: Reset returns to starting position, game_over=False
  - Success: All 14 tests present, all FAIL initially

### Implementation for BoardManager

- [ ] T012 ⏱️ 2h [US1] Implement BoardManager class in chess_agent/board_manager.py
  - Requirements from plan.md:
    * `__init__(fen: str)`: Initialize with FEN (validate)
    * `get_board_copy() → chess.Board`: Deep copy for safe lookahead
    * `get_legal_moves() → List[chess.Move]`: Return all legal moves
    * `make_move(move: chess.Move) → bool`: Apply move, update history atomically
    * `validate_move(move: chess.Move) → bool`: Read-only validation
    * `is_checkmate() → bool`, `is_stalemate() → bool`, `is_draw() → bool`: Termination checks
    * `get_fen() → str`: Return current position
    * `parse_move(move_str: str) → Optional[chess.Move]`: Parse SAN/UCI notation
    * `get_move_history() → List[chess.Move]`: Return immutable copy of history
    * `get_san_move(move: chess.Move) → str`: Convert to standard algebraic notation
    * `reset() → None`: Return to starting position
  - Critical: **Board state NEVER mutated during lookahead** (only via `make_move()`)
  - Docstrings: All methods documented with examples
  - Success: All tests T009, T010 PASS; 100% coverage of board_manager.py
  - Code Review Checkpoint: Verify immutability guarantees, no direct board exposure

- [ ] T013 [P] ⏱️ 2h [US1] Implement DecisionEngine.select_move() and evaluate_position() stubs
  - Location: `chess_agent/decision_engine.py` (update from T006)
  - Methods remain abstract (abstract methods, docstrings with contracts)
  - Success: DecisionEngine interface complete, ready for HeuristicEngine implementation

### Unit Tests for HeuristicEngine (TDD - Write First)

- [ ] T014 ⏱️ 1h [US1] Create unit test suite for heuristic_engine.py
  - Location: `tests/unit/test_heuristic_engine.py`
  - Tests (must FAIL before implementation):
    * `test_engine_name`: Returns "HeuristicEngine"
    * `test_select_move_returns_legal_move`: Selected move is in legal_moves
    * `test_select_move_single_legal_move`: Returns only legal move
    * `test_select_move_empty_returns_none`: Returns None when no legal moves
    * `test_select_move_completed_under_100ms`: Completes depth 3 search in <100ms
    * `test_evaluate_position_white_advantage`: Evaluates white ahead when white has material
    * `test_evaluate_position_black_advantage`: Evaluates black ahead when black has material
    * `test_evaluate_position_equal`: Evaluates 0 for equal material
    * `test_piece_values_pawn`: Pawn = 100
    * `test_piece_values_knight`: Knight = 320
    * `test_piece_values_bishop`: Bishop = 330
    * `test_piece_values_rook`: Rook = 500
    * `test_piece_values_queen`: Queen = 900
  - Success: All 13 tests present, all FAIL initially

- [ ] T015 ⏱️ 2h [US1] Implement HeuristicEngine class in chess_agent/engines/heuristic_engine.py
  - Requirements from plan.md:
    * Inherit from DecisionEngine
    * `__init__()`: Initialize engine (no parameters)
    * `select_move(board: chess.Board) → Optional[chess.Move]`: Minimax depth 3 with alpha-beta pruning
    * `evaluate_position(board: chess.Board) → float`: Material count - based on PIECE_VALUES
    * `_minimax(board, depth, is_maximizing) → float`: Minimax implementation with alpha-beta
    * `PIECE_VALUES` class constant: Pawn=100, Knight=320, Bishop=330, Rook=500, Queen=900
  - Board safety: All evaluations use `board.copy()` or immutable operations
  - Performance: Must complete depth 3 evaluation in <100ms typical positions
  - Success: All tests T014 PASS; 100% coverage of heuristic_engine.py
  - Code Review Checkpoint: Verify minimax correctness, no board mutations, pruning working

### Unit Tests for GameEngine (TDD - Write First)

- [ ] T016 ⏱️ 1.5h [US1] Create unit test suite for game_engine.py (if not already created in T011)
  - Location: `tests/unit/test_game_engine.py`
  - See T011 for test list
  - Success: All 14 tests present, all FAIL initially

### Implementation for GameEngine

- [ ] T017 ⏱️ 2.5h [US1] Implement GameEngine class in chess_agent/game_engine.py
  - Requirements from plan.md:
    * `__init__(board_manager: BoardManager, decision_engine: DecisionEngine)`: Initialize
    * `play_human_move(move_str: str) → Tuple[bool, str]`: Human move with validation, triggers agent response
    * `play_agent_move() → str`: Agent selects and executes move in SAN notation
    * `_check_game_over() → bool`: Detect checkmate, stalemate, draws; set result
    * `is_game_over() → bool`: Query game state
    * `get_result() → Optional[str]`: Return '1-0', '0-1', '1/2-1/2', or None
    * `get_board_fen() → str`: Get position
    * `reset() → None`: Reset to start
  - Safety: Decision engine receives only `board.copy()` via `board_manager.get_board_copy()`
  - Invariants: Strict turn alternation, immutable game state
  - Docstrings: All methods documented with examples
  - Success: All tests T011 PASS; 100% coverage of game_engine.py
  - Code Review Checkpoint: Verify turn alternation, end-game detection, engine receives only copies

### Integration Tests for Complete Game (TDD - Write First)

- [ ] T018 ⏱️ 1.5h [US1] Create integration test suite for complete games
  - Location: `tests/integration/test_complete_game.py`
  - Tests (must FAIL before implementation):
    * `test_complete_game_white_wins`: Play game to white checkmate, verify result='1-0'
    * `test_complete_game_black_wins`: Play game to black checkmate, verify result='0-1'
    * `test_complete_game_stalemate`: Play to stalemate, verify result='1/2-1/2'
    * `test_complete_game_insufficient_material`: End with K vs K, verify draw
    * `test_game_reset_mid_game`: Reset after several moves, start over
  - Success: All 5 tests present, all FAIL initially

### Fix & Validate Phase 3

- [ ] T019 ⏱️ 3h [US1] Run all Phase 3 tests, fix failures, validate 90%+ coverage
  - Run: `pytest tests/unit/test_board_manager.py tests/unit/test_move_validation.py tests/unit/test_game_engine.py tests/unit/test_heuristic_engine.py tests/integration/test_complete_game.py -v --cov=chess_agent`
  - Fix any failing tests
  - Verify coverage: board_manager.py ≥95%, game_engine.py ≥95%, heuristic_engine.py ≥90%
  - Success: All tests PASS, coverage ≥90%, game can play complete legal games
  - Code Review Checkpoint: Manual review of move validation, engine decisions, edge case handling

---

## Phase 4: User Story 2 - CLI Interface (Priority: P2)

**Goal**: Build interactive command-line interface for human vs. agent gameplay  
**Independent Test**: Launch CLI, enter moves, observe board updates, verify hint/eval commands work  
**Note**: Depends on Phase 3 completion (board_manager, game_engine, heuristic_engine)

### Unit Tests for API (TDD - Write First)

- [ ] T020 ⏱️ 1h [US2] Create unit test suite for api.py Agent class
  - Location: `tests/unit/test_api.py`
  - Tests (must FAIL before implementation):
    * `test_agent_init_default_engine`: Initializes with HeuristicEngine
    * `test_agent_init_custom_engine`: Accepts custom engine
    * `test_make_move_valid`: Returns True for valid move
    * `test_make_move_invalid`: Returns False for invalid move
    * `test_get_agent_move_returns_san`: Returns move in standard algebraic notation
    * `test_get_agent_move_game_over`: Returns None when game over
    * `test_get_board_state_returns_fen`: Returns FEN string
    * `test_get_legal_moves_returns_san_list`: Returns list of SAN moves
    * `test_get_evaluation_returns_float`: Returns numeric score
    * `test_is_game_over_false_at_start`: Returns False initially
    * `test_is_game_over_true_at_end`: Returns True after checkmate
    * `test_get_result_none_at_start`: Returns None initially
    * `test_get_result_returns_value_at_end`: Returns '1-0', '0-1', or '1/2-1/2'
    * `test_reset_clears_state`: reset() resets to start
    * `test_set_engine_swaps_engine`: set_engine() changes decision engine
  - Success: All 15 tests present, all FAIL initially

- [ ] T021 [P] ⏱️ 1h [US2] Create unit test suite for cli.py
  - Location: `tests/unit/test_cli.py`
  - Tests (must FAIL before implementation):
    * `test_cli_init`: ChessAgentCLI initializes with Agent
    * `test_display_board_outputs_position`: display_board() prints ASCII board
    * `test_display_board_outputs_fen`: display_board() prints FEN
  - Success: All 3 tests present, all FAIL initially

### Implementation for API & CLI

- [ ] T022 ⏱️ 1.5h [US2] Implement Agent class in chess_agent/api.py
  - Requirements from plan.md:
    * `__init__(engine: Optional[DecisionEngine] = None)`: Initialize with engine (default HeuristicEngine)
    * `make_move(move: str) → bool`: Parse and execute move, return success
    * `get_agent_move() → Optional[str]`: Get engine's selected move in SAN
    * `get_board_state() → str`: Return FEN
    * `get_legal_moves() → List[str]`: Return all legal moves in SAN
    * `get_evaluation() → float`: Return position evaluation
    * `is_game_over() → bool`: Query game state
    * `get_result() → Optional[str]`: Return result
    * `reset() → None`: Reset game
    * `set_engine(engine: DecisionEngine) → None`: Swap engine
  - Docstrings: All methods documented with examples
  - Success: All tests T020 PASS; 100% coverage of api.py
  - Code Review Checkpoint: Verify API contract, engine swapping mechanism

- [ ] T023 [P] ⏱️ 1.5h [US2] Implement ChessAgentCLI class in chess_agent/cli.py
  - Requirements from plan.md:
    * `__init__()`: Initialize CLI with Agent
    * `display_board() → None`: Print ASCII board and FEN
    * `run() → None`: Main game loop
    * Commands: move (e.g., "e4"), 'hint' (suggest move), 'eval' (position score), 'quit' (exit)
    * Move entry: Accept SAN notation ("e4", "Nf3", "O-O") and UCI ("e2e4")
  - User feedback: Error messages for invalid input, move confirmations
  - Success: All tests T021 PASS; basic CLI functional
  - Code Review Checkpoint: Verify user experience, error handling, command parsing

### Integration Tests for CLI

- [ ] T024 ⏱️ 1.5h [US2] Create integration test suite for CLI interaction
  - Location: `tests/integration/test_cli_interaction.py`
  - Tests (must FAIL before implementation):
    * `test_cli_displays_starting_position`: CLI shows starting board
    * `test_cli_accepts_move_san_notation`: User enters "e4", board updates
    * `test_cli_accepts_move_uci_notation`: User enters "e2e4", board updates
    * `test_cli_rejects_invalid_move`: Invalid move shows error, board unchanged
    * `test_cli_hint_command`: 'hint' shows suggested move
    * `test_cli_eval_command`: 'eval' shows position score
    * `test_cli_quit_command`: 'quit' exits gracefully
  - Success: All 7 tests present, all FAIL initially

### Fix & Validate Phase 4

- [ ] T025 ⏱️ 2h [US2] Run all Phase 4 tests, fix failures, validate coverage
  - Run: `pytest tests/unit/test_api.py tests/unit/test_cli.py tests/integration/test_cli_interaction.py -v --cov=chess_agent`
  - Fix any failing tests
  - Verify coverage: api.py ≥95%, cli.py ≥90%
  - Manual test: Run CLI, play a complete game via command-line
  - Success: All tests PASS, CLI fully functional, coverage ≥90%
  - Code Review Checkpoint: Review CLI implementation, user experience, command handling

---

## Phase 5: User Story 3 - Programmatic Python API (Priority: P2)

**Goal**: Verify Agent API works independently for programmatic integration  
**Independent Test**: Import Agent as library, call methods directly, verify behavior without CLI  
**Note**: Depends on Phase 3 completion (Agent class built in US2, but tested here independently)

### Integration Tests for Programmatic API

- [ ] T026 ⏱️ 1h [US3] Create integration test suite for programmatic API
  - Location: `tests/integration/test_programmatic_api.py`
  - Tests (must FAIL before implementation):
    * `test_api_import_agent`: Can import Agent from chess_agent
    * `test_api_basic_game_workflow`: Initialize, make moves, check state, reset (end-to-end)
    * `test_api_move_sequence`: Play sequence of moves programmatically, verify history
    * `test_api_board_immutability`: get_board_state() doesn't expose mutable board
    * `test_api_evaluation_consistent`: Same position evaluated same way multiple times
    * `test_api_multiple_agent_instances`: Two agents don't interfere
    * `test_api_get_legal_moves_format`: Legal moves are SAN strings, all valid
  - Success: All 7 tests present, all FAIL initially

### Fix & Validate Phase 5

- [ ] T027 ⏱️ 1h [US3] Run Phase 5 tests, fix failures, validate API stability
  - Run: `pytest tests/integration/test_programmatic_api.py -v --cov=chess_agent.api`
  - Fix any failing tests
  - Success: All tests PASS, API stable and usable as library
  - Code Review Checkpoint: Verify API contract stability, no breaking changes during game flow

---

## Phase 6: User Story 4 - Swappable Decision Engine (Priority: P3)

**Goal**: Verify architecture supports engine swapping without breaking core logic  
**Independent Test**: Create mock engine, swap at runtime, verify agent behavior changes  
**Note**: Depends on Phase 3+ completion (DecisionEngine interface, GameEngine)

### Unit Tests for Engine Swapping

- [ ] T028 ⏱️ 1h [US4] Create unit test suite for decision engine interface and swapping
  - Location: `tests/unit/test_engine_interface.py`
  - Tests (must FAIL before implementation):
    * `test_decision_engine_is_abstract`: Cannot instantiate DecisionEngine directly
    * `test_heuristic_engine_implements_interface`: HeuristicEngine implements all abstract methods
    * `test_engine_select_move_contract`: select_move() doesn't mutate input board
    * `test_engine_evaluate_contract`: evaluate_position() returns float
  - Success: All 4 tests present, all FAIL initially

- [ ] T029 [P] ⏱️ 1h [US4] Create integration test suite for engine swapping
  - Location: `tests/integration/test_engine_swapping.py`
  - Tests (must FAIL before implementation):
    * `test_swap_engine_default_to_heuristic`: Agent starts with HeuristicEngine
    * `test_swap_engine_to_mock`: set_engine() accepts and uses new engine
    * `test_different_engines_different_moves`: MockEngine1 and MockEngine2 select different moves from same position
    * `test_swap_engine_mid_game`: Swap engine during game, new engine used for next move
    * `test_swap_engine_preserves_board_state`: Board state unchanged after engine swap
    * `test_custom_engine_implementation`: Create dummy engine, swap, verify game continues
  - Notes: Includes MockEngine fixture for testing
  - Success: All 6 tests present, all FAIL initially

### Implementation for Engine Swapping

- [ ] T030 ⏱️ 30m [US4] Ensure DecisionEngine interface supports swapping (verify from T006)
  - Verify: Abstract methods allow any implementation
  - Verify: Agent.set_engine() can swap at runtime
  - Verify: GameEngine doesn't assume specific engine type
  - Success: Architecture verified to support swapping

### Fixtures for Mock Engines

- [ ] T031 [P] ⏱️ 1h [US4] Create mock engine implementations in tests/fixtures/mock_engines.py
  - Implementations:
    * `AlwaysFirstMoveEngine`: Selects first legal move (deterministic)
    * `AlwaysLastMoveEngine`: Selects last legal move (different from first)
  - Success: Mock engines ready for use in engine swapping tests

### Fix & Validate Phase 6

- [ ] T032 ⏱️ 1.5h [US4] Run Phase 6 tests, fix failures, validate engine swapping
  - Run: `pytest tests/unit/test_engine_interface.py tests/integration/test_engine_swapping.py -v --cov=chess_agent`
  - Fix any failing tests
  - Manual verification: Swap engines in CLI, verify different behavior
  - Success: All tests PASS, engine swapping fully functional
  - Code Review Checkpoint: Verify interface design, engine injection, no coupling to specific engine

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final touches, code quality, documentation, coverage validation

### Documentation & Code Quality

- [ ] T033 ⏱️ 1h Create comprehensive docstrings for all public APIs
  - Update all classes/methods in api.py, board_manager.py, game_engine.py, cli.py
  - Format: Google-style docstrings with Args, Returns, Examples, Raises
  - Success: All public methods have docstrings with examples

- [ ] T034 [P] ⏱️ 1h Create README.md with quickstart guide
  - Location: `README.md` (project root)
  - Sections: Features, Installation, Quick Start, CLI Usage, Programmatic API, Examples, Architecture
  - Success: Users can install and run within 5 minutes via README

- [ ] T035 [P] ⏱️ 30m Create ARCHITECTURE.md explaining module relationships
  - Location: `ARCHITECTURE.md` (project root)
  - Sections: Module Overview, Dependency Graph, Data Flow, Board State Safety, Engine Swapping
  - Success: New developers can understand architecture from docs

### Performance Validation

- [ ] T036 ⏱️ 1h Create performance test for move evaluation time
  - Location: `tests/performance/test_performance.py`
  - Test: `test_minimax_depth3_under_2_seconds`: Evaluate typical middlegame position in <2 seconds
  - Test: `test_move_generation_under_100ms`: Generate legal moves in <100ms
  - Success: Both targets met for representative positions

### Final Coverage & Quality Check

- [ ] T037 ⏱️ 2h Run full test suite, validate coverage, fix any remaining issues
  - Run: `pytest tests/ -v --cov=chess_agent --cov-report=html --cov-report=term-missing`
  - Coverage target: ≥90% overall, ≥95% for core modules (board_manager, game_engine)
  - Fix failing tests or coverage gaps
  - Generate HTML coverage report
  - Success: All tests PASS, coverage ≥90%, no coverage gaps in critical code

- [ ] T038 [P] ⏱️ 1h Create test summary report
  - Summary: Total tests run, pass/fail counts, coverage percentages by module
  - Location: `TEST_SUMMARY.md` (project root)
  - Success: Report clearly documents testing completeness

### Code Review Checkpoints Throughout

- [ ] T039 ⏱️ 2h Conduct final code review of all implementation
  - Checklist:
    * All tests PASS ✓
    * Coverage ≥90% ✓
    * No board state mutations during lookahead ✓
    * DecisionEngine interface supports swapping ✓
    * All public methods have docstrings with examples ✓
    * Move validation correct for en passant, castling, promotion, draws ✓
    * Game end detection correct (checkmate, stalemate, draws) ✓
    * CLI and API both functional ✓
    * Performance targets met (<2s evaluation) ✓
  - Success: Code ready for production use

---

## Dependencies & Parallel Execution Opportunities

### Dependency Graph

```
T001-T005 (Setup) ✓
    ↓
T006-T008 (Foundational Interfaces) ✓
    ↓
Phase 3: US1 (Complete Game)
    ├─ T009-T011 (Unit tests - can run in parallel) → T012-T015 (Implementation)
    │   ├─ T012 (BoardManager) → T017 (GameEngine)
    │   └─ T014-T015 (HeuristicEngine)
    ├─ T018 (Integration tests) → T019 (Validate)
    ↓
Phase 4: US2 (CLI)
    ├─ T020-T021 (Unit tests) → T022-T023 (Implementation)
    ├─ T024 (Integration tests) → T025 (Validate)
    ↓
Phase 5: US3 (API)
    ├─ T026 (Integration tests) → T027 (Validate)
    ↓
Phase 6: US4 (Swappable Engine)
    ├─ T028-T029 (Tests) → T030-T031 (Implementation)
    ├─ T032 (Validate)
    ↓
Phase 7: Polish
    ├─ T033-T038 (Documentation, performance, final validation)
```

### Parallel Execution by Phase

**Phase 1** (Setup): All independent
- Parallel: T001, T002-T005 (all can start simultaneously)
- **Duration**: 1.5h total (50m setup + 40m deps)

**Phase 2** (Foundational): T006-T008 mostly independent
- Parallel: T007-T008 (can run while T006 in progress)
- **Duration**: 1.5h total

**Phase 3** (US1 - MVP): **Critical Path**
- **Parallel Wave 1** (Tests): T009-T011 (3 parallel test suites: 3h for 1 developer)
- **Sequential** (Implementation): T012 → T013, then T014 → T015, then T016 → T017
- **Sequential** (Integration): T018, then T019
- **Total Duration**: ~7.5h critical path (tests can be written in parallel with T012-T015 implementation)
- **Opportunity**: Start tests T009-T011 while T012 implementation in progress

**Phase 4** (US2 - CLI): Depends on Phase 3
- **Parallel**: T020-T021 (2 parallel test suites: 2h)
- **Parallel**: T022-T023 (2 parallel implementations: 3h)
- **Sequential**: T024 → T025
- **Total Duration**: ~3.5h (tests and implementation can overlap)

**Phase 5** (US3 - API): Depends on Phase 4
- **Sequential**: T026 → T027
- **Total Duration**: ~1.5h

**Phase 6** (US4 - Swappable Engine): Depends on Phase 3
- **Parallel**: T028-T029 (2 parallel test suites: 2h)
- **Parallel**: T031 (mock engines: 1h, can start immediately)
- **Sequential**: T030, T032
- **Total Duration**: ~2.5h

**Phase 7** (Polish): Depends on Phases 3-6
- **Parallel**: T033-T035, T036, T038 (can run simultaneously: 4h)
- **Sequential**: T037 (final validation: 2h)
- **Total Duration**: ~4h

### Total Effort Estimation

| Phase | Tasks | Duration | Critical Path |
|-------|-------|----------|---|
| 1 - Setup | T001-T005 | 1.5h | Sequential |
| 2 - Foundational | T006-T008 | 1.5h | Sequential |
| 3 - US1 (MVP) | T009-T019 | 8h | CRITICAL |
| 4 - US2 (CLI) | T020-T025 | 4h | Depends on Phase 3 |
| 5 - US3 (API) | T026-T027 | 1.5h | Depends on Phase 4 |
| 6 - US4 (Engine) | T028-T032 | 2.5h | Depends on Phase 3 |
| 7 - Polish | T033-T039 | 5h | Depends on Phases 3-6 |
| **TOTAL** | 39 tasks | **~24h** (critical path) | ~1-2 days for experienced developer |

### Recommended MVP Scope (Phase 3 Only)

For minimum viable product, complete **Phase 3** (User Story 1):
- Core game engine with board state management ✓
- Move validation with edge case handling ✓
- Heuristic decision engine ✓
- Complete game playback ✓
- Integration testing ✓
- **Duration**: ~8 hours
- **Coverage**: ~90%
- **Deliverable**: Autonomous agent that can play complete legal chess games

### Suggested Implementation Order for Single Developer

1. **Day 1 Morning**: Phases 1-2 (Setup + Foundational) — 3h
2. **Day 1 Afternoon**: Phase 3 US1 (MVP Game Engine) — 8h
3. **Day 2 Morning**: Phase 4 US2 (CLI) — 4h
4. **Day 2 Afternoon**: Phase 5 US3 (API) + Phase 6 US4 (Engine Swapping) — 4h
5. **Day 3**: Phase 7 (Polish + Final Validation) — 5h
6. **Total**: ~24 hours spread over 2-3 days

---

## Success Criteria by Phase

### Phase 3 (MVP - US1) ✓ CRITICAL
- [ ] All 18 BoardManager tests PASS
- [ ] All 22 move validation edge case tests PASS
- [ ] All 14 GameEngine tests PASS
- [ ] All 13 HeuristicEngine tests PASS
- [ ] All 5 complete game integration tests PASS
- [ ] Coverage ≥90% (core modules ≥95%)
- [ ] Agent can play complete legal games
- [ ] All code reviewed

### Phase 4 (US2)
- [ ] All 15 API tests PASS
- [ ] All 3 CLI unit tests PASS
- [ ] All 7 CLI integration tests PASS
- [ ] Coverage ≥90%
- [ ] CLI fully functional (moves, hints, eval, quit)
- [ ] User can play complete game via CLI

### Phase 5 (US3)
- [ ] All 7 programmatic API tests PASS
- [ ] Agent importable and usable as library
- [ ] Multiple agent instances independent
- [ ] API stable across full game lifecycle

### Phase 6 (US4)
- [ ] All 4 engine interface tests PASS
- [ ] All 6 engine swapping tests PASS
- [ ] Mock engines work correctly
- [ ] Different engines produce different moves
- [ ] Engine swap mid-game works

### Phase 7 (Polish)
- [ ] All docstrings complete
- [ ] README and ARCHITECTURE docs complete
- [ ] Performance tests all PASS (< 2 seconds)
- [ ] Final coverage ≥90%
- [ ] Code review complete
- [ ] Test summary report generated
- [ ] Ready for production use
