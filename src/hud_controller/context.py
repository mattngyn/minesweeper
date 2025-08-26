"""Minesweeper game context that persists across hot-reloads."""
from hud.server.context import run_context_server
import asyncio
from .minesweeper import MinesweeperGame

class Context:
    def __init__(self):
        self.game = MinesweeperGame()
        self.games_played = 0
        self.games_won = 0
    
    def new_game(self, rows: int = 9, cols: int = 9, num_mines: int = 10):
        """Start a new minesweeper game."""
        result = self.game.setup_game(rows, cols, num_mines)
        self.games_played += 1
        return result
    
    def reveal_cell(self, row: int, col: int):
        """Reveal a cell in the current game."""
        result = self.game.reveal(row, col)
        if result.get("won", False):
            self.games_won += 1
        return result
    
    def flag_cell(self, row: int, col: int):
        """Flag or unflag a cell in the current game."""
        return self.game.flag(row, col)
    
    def get_board_state(self):
        """Get the current board state."""
        return self.game.get_board()
    
    def get_game_state(self):
        """Get complete game state for evaluation."""
        state = self.game.get_game_state()
        state["games_played"] = self.games_played
        state["games_won"] = self.games_won
        state["win_rate"] = self.games_won / max(1, self.games_played)
        return state

if __name__ == "__main__":
    asyncio.run(run_context_server(Context()))
