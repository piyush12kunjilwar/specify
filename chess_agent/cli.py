"""Command-line interface for playing chess against the autonomous agent."""

import sys
from typing import Optional
from chess_agent.board_manager import BoardManager
from chess_agent.game_engine import GameEngine
from chess_agent.engines import HeuristicEngine


def display_board(board_fen: str) -> None:
    """Display the chess board in a human-readable format."""
    from chess import Board
    board = Board(board_fen)
    print(board)


def display_info(game: GameEngine, board_manager: BoardManager) -> None:
    """Display game information: board, status, legal moves."""
    print("\n" + "=" * 50)
    display_board(game.get_board_fen())
    
    legal_moves = board_manager.get_legal_moves()
    print(f"\nLegal moves ({len(legal_moves)}): ", end="")
    print(" ".join([board_manager.get_san_move(m) for m in legal_moves[:10]]), end="")
    if len(legal_moves) > 10:
        print(f" ... ({len(legal_moves) - 10} more)")
    else:
        print()
    
    result = game.get_result()
    if result:
        print(f"\nResult: {result}")
    
    print("=" * 50)


def print_welcome() -> None:
    """Print welcome message."""
    print("\n" + "=" * 50)
    print("    AUTONOMOUS CHESS AGENT")
    print("=" * 50)
    print("Play chess against the autonomous agent!")
    print("\nCommands:")
    print("  <move>  - Play a move (e.g., 'e4', 'Nf3', 'O-O')")
    print("  hint    - Get a suggested move")
    print("  board   - Display the board")
    print("  moves   - List all legal moves")
    print("  reset   - Start a new game")
    print("  quit    - Exit the game")
    print("=" * 50 + "\n")


def main() -> None:
    """Main CLI loop for playing chess against the agent."""
    # Initialize game components
    board_manager = BoardManager()
    engine = HeuristicEngine()
    game = GameEngine(board_manager, engine)
    
    print_welcome()
    display_info(game, board_manager)
    
    move_number = 1
    while True:
        try:
            # Prompt for user input
            prompt = f"Move {move_number}. Your move: " if board_manager.get_board_copy().turn else f"Move {move_number}. Agent's turn: "
            user_input = input(prompt).strip().lower()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input == 'quit':
                print("\nThanks for playing! Goodbye.")
                break
            
            elif user_input == 'reset':
                board_manager.reset()
                game = GameEngine(board_manager, engine)
                move_number = 1
                print("\nGame reset to starting position.")
                display_info(game, board_manager)
                continue
            
            elif user_input == 'hint':
                board_copy = board_manager.get_board_copy()
                hint_move = engine.select_move(board_copy)
                if hint_move:
                    hint_san = board_manager.get_san_move(hint_move)
                    print(f"Hint: {hint_san}")
                else:
                    print("No legal moves available!")
                continue
            
            elif user_input == 'board':
                display_info(game, board_manager)
                continue
            
            elif user_input == 'moves':
                legal_moves = board_manager.get_legal_moves()
                move_strs = [board_manager.get_san_move(m) for m in legal_moves]
                print(f"\nLegal moves ({len(move_strs)}):")
                for i, m in enumerate(move_strs, 1):
                    print(f"  {i}. {m}", end="")
                    if i % 10 == 0:
                        print()
                    else:
                        print(" ", end="")
                print("\n")
                continue
            
            # Try to play the move
            if not board_manager.get_board_copy().turn:
                # Agent's turn - shouldn't get here
                print("It's the agent's turn!")
                continue
            
            # Parse and execute human move
            move = board_manager.parse_move(user_input)
            if not move:
                print(f"Invalid move notation: '{user_input}'. Please use SAN (e.g., 'e4') or UCI (e.g., 'e2e4') notation.")
                continue
            
            if not board_manager.validate_move(move):
                print(f"Illegal move: '{user_input}'. Please check your move.")
                continue
            
            # Get SAN notation before making the move
            move_san = board_manager.get_san_move(move)
            
            # Execute human move
            board_manager.make_move(move)
            game._check_game_over()
            print(f"You played: {move_san}")
            
            # Check if game ended
            if game.is_game_over():
                display_info(game, board_manager)
                result = game.get_result()
                if result == "1-0":
                    print("White wins! Congratulations!")
                elif result == "0-1":
                    print("Black wins! The agent defeated you.")
                elif result == "1/2-1/2":
                    print("Draw!")
                break
            
            # Agent's turn
            print("Agent is thinking...")
            board_copy = board_manager.get_board_copy()
            agent_move = engine.select_move(board_copy)
            
            if not agent_move:
                print("Agent has no legal moves!")
                break
            
            # Get SAN notation before making the move
            agent_move_san = board_manager.get_san_move(agent_move)
            
            # Make the move
            board_manager.make_move(agent_move)
            game._check_game_over()
            print(f"Agent played: {agent_move_san}")
            
            move_number += 1
            
            # Check if game ended
            if game.is_game_over():
                display_info(game, board_manager)
                result = game.get_result()
                if result == "1-0":
                    print("White wins!")
                elif result == "0-1":
                    print("Black wins!")
                elif result == "1/2-1/2":
                    print("Draw!")
                break
            
            display_info(game, board_manager)
        
        except KeyboardInterrupt:
            print("\n\nGame interrupted. Thanks for playing!")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue


if __name__ == "__main__":
    main()
