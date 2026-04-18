import customtkinter as ctk
import chess
import threading
from agent import ChessAgent

class ChessGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Magus Autonomous Chess Agent")
        self.geometry("650x750")
        ctk.set_appearance_mode("dark")
        
        self.agent = ChessAgent()
        self.selected_square = None
        self.buttons = {}
        
        # Map python-chess letters to standard Unicode chess pieces
        self.piece_unicode = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
            None: ''
        }
        
        self.create_widgets()
        self.update_board()

    def create_widgets(self):
        # Header/Status Bar
        self.status_label = ctk.CTkLabel(self, text="Status: White to Move", font=("Arial", 24, "bold"))
        self.status_label.pack(pady=20)
        
        # Board Container
        self.board_frame = ctk.CTkFrame(self, corner_radius=10)
        self.board_frame.pack(expand=True)
        
        # Draw 8x8 Grid
        for rank in range(7, -1, -1):
            for file in range(8):
                square = chess.square(file, rank)
                # Standard chess board coloring (Light = #EEEED2, Dark = #769656)
                color = "#EEEED2" if (rank + file) % 2 != 0 else "#769656"
                
                btn = ctk.CTkButton(
                    self.board_frame, 
                    text="", 
                    width=70, 
                    height=70,
                    corner_radius=0,
                    fg_color=color,
                    text_color="black",
                    hover_color="#F6F669", # Highlight yellow on hover
                    font=("Arial", 46),
                    command=lambda s=square: self.on_square_click(s)
                )
                btn.grid(row=7-rank, column=file, padx=0, pady=0)
                self.buttons[square] = btn

    def on_square_click(self, square):
        # Ignore clicks if game is over or if it's the agent's (Black's) turn
        if self.agent.get_game_status() != "In Progress" or self.agent.board.turn != chess.WHITE:
            return
            
        if self.selected_square is None:
            piece = self.agent.board.piece_at(square)
            if piece and piece.color == chess.WHITE:
                self.selected_square = square
                self.update_board() # Reset colors
                self.buttons[square].configure(fg_color="#F6F669") # Highlight selected
        else:
            move = chess.Move(self.selected_square, square)
            
            # Auto-Queen on pawn promotion for simplicity in the GUI MVP
            if self.agent.board.piece_at(self.selected_square).piece_type == chess.PAWN and chess.square_rank(square) == 7:
                move.promotion = chess.QUEEN

            if move in self.agent.board.legal_moves:
                san_move = self.agent.board.san(move)
                self.agent.make_move(san_move)
                self.selected_square = None
                self.update_board()
                self.check_status()
                
                if self.agent.get_game_status() == "In Progress":
                    self.status_label.configure(text="Agent is thinking...")
                    # Execute agent's move in a background thread to prevent UI freezing (Rule I & III compliance)
                    threading.Thread(target=self.agent_turn, daemon=True).start()
            else:
                # If illegal move, just deselect or reselect a new piece
                self.selected_square = None
                self.update_board()

    def agent_turn(self):
        self.agent.apply_agent_move()
        # Safely schedule GUI updates back on the main thread
        self.after(0, self.update_board)
        self.after(0, self.check_status)

    def check_status(self):
        status = self.agent.get_game_status()
        self.status_label.configure(text=f"Status: {status}" if status != "In Progress" else "Status: White to Move")

    def update_board(self):
        for square, btn in self.buttons.items():
            color = "#EEEED2" if (chess.square_rank(square) + chess.square_file(square)) % 2 != 0 else "#769656"
            piece = self.agent.board.piece_at(square)
            btn.configure(text=self.piece_unicode[piece.symbol() if piece else None], fg_color=color)

if __name__ == "__main__":
    app = ChessGUI()
    app.mainloop()