# Quickstart Guide: Autonomous Chess Agent

**Date**: 2026-04-17  
**Target Audience**: Developers integrating or extending the chess agent  
**Status**: Complete

---

## Installation & Setup

### 1. Install Dependencies

```bash
# Clone/initialize project (from repository root)
pip install -r requirements.txt
```

**requirements.txt**:
```
python-chess==1.9.4
pytest==7.4.0
pytest-cov==4.1.0
pytest-mock==3.11.1
```

### 2. Verify Installation

```bash
# Run tests to verify setup
pytest tests/ -v --cov=chess_agent --cov-report=term-missing
```

Expected output:
```
collected 50+ tests
tests/unit/test_board_manager.py::test_initialize ... PASSED
tests/unit/test_game_engine.py::test_play_human_move ... PASSED
... (all tests pass)

---------- coverage: platform linux -- Python 3.9.x -----------
chess_agent/board_manager.py         18      0    100%
chess_agent/game_engine.py           25      0    100%
... total                            200      5     97%
```

---

## Using the Programmatic API

### Scenario 1: Play a Complete Game Against Agent

```python
from chess_agent import Agent

# Initialize agent with default heuristic engine
agent = Agent()

# Play opening move
if agent.make_move("e2e4"):
    print(f"✓ Your move: e4")
    print(f"Agent plays: {agent.get_agent_move()}")
else:
    print("✗ Invalid move")

# Continue game loop
while not agent.is_game_over():
    # Your move
    your_move = input("Your move: ")
    if agent.make_move(your_move):
        if agent.is_game_over():
            print(f"Game Over. Result: {agent.get_result()}")
            break
        
        # Agent's move
        agent_move = agent.get_agent_move()
        print(f"Agent plays: {agent_move}")
    else:
        print("Invalid move. Legal moves:", agent.get_legal_moves())

print(f"\nFinal Result: {agent.get_result()}")
```

**Output Example**:
```
✓ Your move: e4
Agent plays: e5

Your move: Nf3
Agent plays: Nf6

Your move: Nc3
Agent plays: Nc6

Your move: Bc4
Agent plays: Bc5

Your move: illegal_move
Invalid move. Legal moves: ['d3', 'Nxe5', 'Bg5', ...]

Your move: d3
Agent plays: O-O

... (game continues)

Game Over. Result: 1/2-1/2 (draw)
```

### Scenario 2: Get Position Evaluation & Hints

```python
from chess_agent import Agent

agent = Agent()

# Make some moves
agent.make_move("e2e4")
agent.get_agent_move()

# Get position evaluation
score = agent.get_evaluation()
print(f"Position evaluation: {score:+.1f} (positive = advantage for current player)")

# Get legal moves
legal_moves = agent.get_legal_moves()
print(f"Legal moves ({len(legal_moves)}): {', '.join(legal_moves[:5])}...")

# Get current position
fen = agent.get_board_state()
print(f"FEN: {fen}")
```

**Output Example**:
```
Position evaluation: +25.0 (positive = advantage for current player)
Legal moves (20): e5, d5, c5, Nf6, Nc6...
FEN: rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2
```

### Scenario 3: Swapping Decision Engines at Runtime

```python
from chess_agent import Agent
from chess_agent.engines import HeuristicEngine, RandomEngine

# Start with heuristic engine
agent = Agent(engine=HeuristicEngine())
heuristic_move = agent.get_agent_move()

# Reset and try random engine
agent.reset()
agent.set_engine(RandomEngine())
random_move = agent.get_agent_move()

print(f"Heuristic engine selected: {heuristic_move}")
print(f"Random engine selected: {random_move}")
print(f"Engines may differ: {heuristic_move != random_move}")
```

**Output Example**:
```
Heuristic engine selected: e5
Random engine selected: c5
Engines may differ: True
```

### Scenario 4: Custom Engine Integration (Future - LLM)

```python
from chess_agent import Agent, DecisionEngine
import chess

class LLMEngine(DecisionEngine):
    """Future LLM-based engine integration."""
    
    def select_move(self, board: chess.Board) -> chess.Move:
        # TODO: Prompt LLM with position
        # TODO: Parse response to get move
        # For now, fallback to random legal move
        import random
        return random.choice(list(board.legal_moves))
    
    def evaluate_position(self, board: chess.Board) -> float:
        # TODO: Request LLM evaluation
        return 0.0  # Placeholder
    
    def get_engine_name(self) -> str:
        return "LLM-Engine"

# Use custom engine seamlessly
agent = Agent(engine=LLMEngine())
agent.make_move("e2e4")
print(f"LLM engine playing: {agent.get_agent_move()}")
```

---

## Using the CLI Interface

### Starting an Interactive Game

```bash
# From repository root
python -m chess_agent.cli
```

**Interactive Session**:
```
Chess Agent - Type 'help' for commands

  ♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜
  ♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟
  · · · · · · · ·
  · · · · · · · ·
  · · · · · · · ·
  · · · · · · · ·
  ♙ ♙ ♙ ♙ ♙ ♙ ♙ ♙
  ♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖

FEN: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

Your move (or command): e2e4
✓ Agent plays: e5

(board display updates)

Your move (or command): hint
Suggested move: Nf3

Your move (or command): Nf3
✓ Agent plays: Nf6

(continue until game over)
```

### CLI Commands

| Command | Syntax | Example | Effect |
|---------|--------|---------|--------|
| Move | SAN or UCI | `e4` or `e2e4` | Make your move |
| Castling | SAN notation | `O-O` or `O-O-O` | Execute castling |
| Promotion | Append piece | `a8=Q` or `a7a8q` | Promote pawn |
| Hint | `hint` | `hint` | Get suggested move |
| Evaluation | `eval` | `eval` | Show position score |
| Reset | `reset` | `reset` | Start new game |
| Quit | `quit` | `quit` | Exit CLI |
| Help | `help` | `help` | Show this help |

---

## Testing & Verification

### Running the Test Suite

```bash
# Run all tests with coverage
pytest tests/ -v --cov=chess_agent

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/unit/test_move_validation.py -v

# Run with detailed output
pytest tests/unit/test_edge_cases.py -vv
```

### Example Test Output

```
tests/unit/test_board_manager.py::test_initialize_starting_position PASSED
tests/unit/test_board_manager.py::test_make_move_valid PASSED
tests/unit/test_board_manager.py::test_make_move_invalid PASSED
tests/unit/test_move_validation.py::test_en_passant_capture PASSED
tests/unit/test_move_validation.py::test_castling_kingside PASSED
tests/unit/test_edge_cases.py::test_threefold_repetition PASSED
tests/integration/test_complete_game.py::test_game_to_checkmate PASSED

---------- coverage report ----------
chess_agent/board_manager.py      18       0    100%
chess_agent/game_engine.py        25       0    100%
chess_agent/decision_engine.py    10       0    100%
chess_agent/engines/heuristic_engine.py    32       1     97%
chess_agent/api.py               15       0    100%

TOTAL                            200       5     97%
```

### Writing Tests for Extensions

```python
# Example: Test a custom engine

from chess_agent import DecisionEngine, Agent
import chess
import pytest

class TestCustomEngine:
    """Test suite for custom engine implementation."""
    
    def test_engine_returns_legal_move(self):
        """Verify engine never returns illegal move."""
        custom_engine = MyCustomEngine()
        board = chess.Board()
        move = custom_engine.select_move(board)
        
        assert move in board.legal_moves, "Engine returned illegal move"
    
    def test_engine_completes_under_time_limit(self):
        """Verify engine meets performance requirement."""
        import time
        custom_engine = MyCustomEngine()
        board = chess.Board()
        
        start = time.time()
        move = custom_engine.select_move(board)
        elapsed = time.time() - start
        
        assert elapsed < 2.0, f"Engine took {elapsed:.2f}s, must be <2s"
    
    def test_integration_with_agent(self):
        """Verify engine works seamlessly with Agent."""
        custom_engine = MyCustomEngine()
        agent = Agent(engine=custom_engine)
        
        # Game should play without errors
        agent.make_move("e2e4")
        move = agent.get_agent_move()
        
        assert move is not None, "Engine failed to select move"
        assert move in agent.get_legal_moves(), "Engine returned illegal move"
```

---

## Architecture & Extension Points

### Module Dependencies

```
agent (Public API)
  ├── board_manager (Board state + validation)
  ├── game_engine (Game orchestration)
  │   ├── decision_engine (Abstract interface)
  │   │   ├── heuristic_engine (Default implementation)
  │   │   └── [custom_engine] (Future extensions)
  │   └── board_manager
  └── cli (Interactive terminal)
```

### Extension Points

**1. Custom Decision Engine**:
```python
from chess_agent import DecisionEngine
import chess

class MyEngine(DecisionEngine):
    def select_move(self, board: chess.Board) -> chess.Move:
        # Your implementation
        pass
    
    def evaluate_position(self, board: chess.Board) -> float:
        # Your implementation
        pass

# Use immediately
agent = Agent(engine=MyEngine())
```

**2. Custom CLI**:
```python
from chess_agent import GameEngine, BoardManager, HeuristicEngine

# Reuse core logic, build custom UI
board = BoardManager()
engine = HeuristicEngine()
game = GameEngine(board, engine)

# Integrate with your UI framework (web, mobile, etc.)
game.play_human_move("e2e4")
```

**3. Analysis & Statistics**:
```python
from chess_agent import Agent

agent = Agent()

# Play game and collect positions
positions = []
while not agent.is_game_over():
    positions.append({
        'fen': agent.get_board_state(),
        'eval': agent.get_evaluation(),
        'legal_moves': len(agent.get_legal_moves())
    })
    # ... make moves

# Analyze game afterwards
average_eval = sum(p['eval'] for p in positions) / len(positions)
print(f"Average position score: {average_eval:+.1f}")
```

---

## Performance Tuning

### Move Evaluation Time

**Target**: <2 seconds per move (opening/middlegame)

**Current Heuristic Engine Configuration**:
```python
# Depth setting in heuristic_engine.py
MINIMAX_DEPTH = 3  # Typical: ~100ms per position
```

**To improve performance**:
```python
# Reduce depth for faster evaluation
MINIMAX_DEPTH = 2  # ~5ms per position (sacrifices strength)

# To increase strength
MINIMAX_DEPTH = 4  # ~1000ms per position (longer thinking time)
```

### Memory Usage

**Typical Memory Footprint**:
- Board state: ~1KB per position
- Move history (100 moves): ~2KB
- Transposition table (if added): Configurable (optional)

**Optimizations Available**:
- Disable move history tracking if not needed
- Use transposition table for repeated positions
- Implement zobrist hashing for fast position lookups

---

## Troubleshooting

### Issue: Import errors when using Agent

```python
# ✗ This fails
from chess_agent import Agent

# ✓ This works
from chess_agent.api import Agent
```

**Solution**: Ensure `__init__.py` exports `Agent` at package level, or use full import path.

### Issue: Move is rejected as illegal

```python
# ✗ Illegal move notation
agent.make_move("e4")  # Returns False (ambiguous pawn move)

# ✓ Correct notation
agent.make_move("e2e4")  # Returns True (UCI format)
agent.make_move("e4")    # If only one pawn can move to e4 (SAN)
```

**Solution**: Use UCI format (from_square + to_square) for clarity, or ensure SAN notation is unambiguous.

### Issue: Agent takes too long to move

```python
# Increase speed, reduce strength
from chess_agent.engines import HeuristicEngine

engine = HeuristicEngine()
engine.MINIMAX_DEPTH = 2  # Faster (but weaker)

# Or check for complex position
board = agent.get_board_state()
legal_move_count = len(agent.get_legal_moves())
print(f"Position complexity: {legal_move_count} legal moves")
```

**Solution**: Reduce minimax depth, or wait for endgame where fewer moves = faster evaluation.

---

## Next Steps

1. **Extend Decision Engine**: Implement custom evaluation algorithm
2. **Build UI Frontend**: Create web interface using game_engine core
3. **Integration Tests**: Test with other chess systems (UCI, PGN export)
4. **Performance Benchmark**: Profile move generation and optimize hotspots
5. **Future LLM Integration**: Follow the CustomEngine pattern when LLM ready

---

## API Reference Quick Links

- **Agent Class**: `chess_agent.api.Agent`
- **DecisionEngine Interface**: `chess_agent.decision_engine.DecisionEngine`
- **BoardManager Class**: `chess_agent.board_manager.BoardManager`
- **GameEngine Class**: `chess_agent.game_engine.GameEngine`
- **HeuristicEngine Class**: `chess_agent.engines.heuristic_engine.HeuristicEngine`

## Support & Resources

- **Python-Chess Docs**: https://python-chess.readthedocs.io/
- **Chess Rules**: https://www.chess.com/terms/chess-rules
- **Test Examples**: See `tests/` directory in repository

---

**Last Updated**: 2026-04-17  
**Version**: 1.0.0-draft
