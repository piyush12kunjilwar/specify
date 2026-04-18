import sys
from agent import ChessAgent

def main():
    print("Welcome to Magus Chess Agent CLI")
    print("================================")
    agent = ChessAgent()
    
    while True:
        print("\n" + str(agent.get_board_state()))
        status = agent.get_game_status()
        if status != "In Progress":
            print(f"\nGame Over: {status}")
            break
            
        user_move = input("\nEnter move (e.g. e4, Nf3) or 'hint' / 'quit': ").strip()
        
        if user_move.lower() == 'quit':
            print("Exiting game. Thanks for playing!")
            break
        elif user_move.lower() == 'hint':
            hint_move = agent.get_next_move()
            board_copy = agent.get_board_state()
            print(f"Agent suggests: {board_copy.san(hint_move) if hint_move else 'None'}")
            continue
            
        if not agent.make_move(user_move):
            print("Invalid or illegal move. Please try again.")
            continue
            
        status = agent.get_game_status()
        if status != "In Progress":
            print("\n" + str(agent.get_board_state()))
            print(f"\nGame Over: {status}")
            break
            
        print("Agent is thinking...")
        agent.apply_agent_move()

if __name__ == "__main__":
    main()