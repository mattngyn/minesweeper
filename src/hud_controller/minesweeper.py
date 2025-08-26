"""
Minesweeper game class for HUD environment.
Wraps the existing game logic from game.py into a clean, stateful class.
"""
import random
import copy
from typing import Tuple, Optional, List, Dict, Any


class MinesweeperGame:
    """Minesweeper game implementation for HUD environment."""
    
    def __init__(self):
        self.grid = []  # Internal number board (-1 for mines, numbers for counts)
        self.display_board = []  # What the player sees ('X', 'F', '-', numbers, '*')
        self.rows = 0
        self.cols = 0
        self.num_mines = 0
        self.game_over = False
        self.won = False
        self.mines_flagged = 0
        
    def setup_game(self, rows: int = 9, cols: int = 9, num_mines: int = 10) -> Dict[str, Any]:
        """Initialize a new minesweeper game with given parameters."""
        if num_mines >= rows * cols:
            raise ValueError("Number of mines must be less than total cells")
        
        self.rows = rows
        self.cols = cols
        self.num_mines = num_mines
        self.game_over = False
        self.won = False
        self.mines_flagged = 0
        
        # Reset boards
        self.grid = []
        self.display_board = []
        
        # Create empty boards
        self._create_board()
        self._assign_bombs()
        self._calculate_mine_indicators()
        
        return {
            "status": "ready",
            "rows": self.rows,
            "cols": self.cols,
            "num_mines": self.num_mines,
            "board": self._get_board_display()
        }
    
    def _create_board(self):
        """Create empty number board and display board."""
        # Create empty number board
        for r in range(self.rows):
            self.grid.append([])
            for c in range(self.cols):
                self.grid[r].append(0)
        
        # Initialize empty display board
        for r in range(self.rows):
            self.display_board.append([])
            for c in range(self.cols):
                self.display_board[r].append('X')  # X = unrevealed
    
    def _assign_bombs(self):
        """Assign mines at random locations."""
        mines_placed = 0
        while mines_placed != self.num_mines:
            mine_row = random.randint(0, self.rows - 1)
            mine_col = random.randint(0, self.cols - 1)
            
            if self.grid[mine_row][mine_col] != -1:
                self.grid[mine_row][mine_col] = -1
                mines_placed += 1
    
    def _calculate_mine_indicators(self):
        """Calculate numbers indicating adjacent mines for each cell."""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] != -1:  # If not a mine
                    mine_count = 0
                    
                    # Check all 8 adjacent cells
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            
                            nr, nc = r + dr, c + dc
                            if (0 <= nr < self.rows and 0 <= nc < self.cols 
                                and self.grid[nr][nc] == -1):
                                mine_count += 1
                    
                    self.grid[r][c] = mine_count
    
    def reveal(self, row: int, col: int) -> Dict[str, Any]:
        """Reveal a cell and return the result."""
        if self.game_over:
            return {"status": "game_over", "message": "Game is already over"}
        
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return {"status": "invalid", "message": "Coordinates out of bounds"}
        
        if self.display_board[row][col] == 'F':
            return {"status": "invalid", "message": "Cannot reveal flagged cell"}
        
        if self.display_board[row][col] != 'X':
            return {"status": "invalid", "message": "Cell already revealed"}
        
        # Hit a mine
        if self.grid[row][col] == -1:
            self.display_board[row][col] = '*'
            self.game_over = True
            return {
                "status": "mine_hit",
                "message": "Game over - you hit a mine!",
                "board": self._get_board_display(),
                "game_over": True,
                "won": False
            }
        
        # Reveal the cell(s)
        self._uncover_squares(row, col)
        
        # Check for win condition
        if self._check_win():
            self.game_over = True
            self.won = True
            return {
                "status": "won",
                "message": "Congratulations! You won!",
                "board": self._get_board_display(),
                "game_over": True,
                "won": True
            }
        
        return {
            "status": "revealed",
            "message": f"Revealed cell ({row}, {col})",
            "board": self._get_board_display(),
            "game_over": False,
            "won": False
        }
    
    def flag(self, row: int, col: int) -> Dict[str, Any]:
        """Flag or unflag a cell."""
        if self.game_over:
            return {"status": "game_over", "message": "Game is already over"}
        
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return {"status": "invalid", "message": "Coordinates out of bounds"}
        
        if self.display_board[row][col] not in ['X', 'F']:
            return {"status": "invalid", "message": "Cannot flag revealed cell"}
        
        if self.display_board[row][col] == 'X':
            # Flag the cell
            self.display_board[row][col] = 'F'
            self.mines_flagged += 1
            message = f"Flagged cell ({row}, {col})"
        else:  # self.display_board[row][col] == 'F'
            # Unflag the cell
            self.display_board[row][col] = 'X'
            self.mines_flagged -= 1
            message = f"Unflagged cell ({row}, {col})"
        
        return {
            "status": "flagged",
            "message": message,
            "board": self._get_board_display(),
            "mines_flagged": self.mines_flagged,
            "game_over": False
        }
    
    def _uncover_squares(self, row: int, col: int):
        """Recursively uncover squares (flood fill for empty areas)."""
        # Check bounds and if already revealed
        if (not (0 <= row < self.rows and 0 <= col < self.cols) 
            or self.display_board[row][col] != 'X'):
            return
        
        # If flagged, don't reveal
        if self.display_board[row][col] == 'F':
            return
        
        # If it has a number, show it
        if self.grid[row][col] > 0:
            self.display_board[row][col] = str(self.grid[row][col])
            return
        
        # If it's empty (0), show as '-' and recursively reveal neighbors
        if self.grid[row][col] == 0:
            self.display_board[row][col] = '-'
            
            # Recursively reveal all 8 adjacent cells
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if (0 <= nr < self.rows and 0 <= nc < self.cols 
                        and self.grid[nr][nc] >= 0):
                        self._uncover_squares(nr, nc)
    
    def _check_win(self) -> bool:
        """Check if the player has won the game."""
        uncovered = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if (self.display_board[r][c] != 'X' 
                    and self.display_board[r][c] != 'F' 
                    and self.display_board[r][c] != '*'):
                    uncovered += 1
        
        # Win if all non-mine cells are uncovered
        return (self.rows * self.cols) - self.num_mines == uncovered
    
    def _get_board_display(self) -> str:
        """Get a formatted string representation of the current board."""
        # Header with column numbers
        header = "   " + " ".join(f"{c:2}" for c in range(self.cols))
        lines = [header]
        
        # Board rows with row numbers
        for r in range(self.rows):
            row_str = f"{r:2} "
            for c in range(self.cols):
                row_str += f" {self.display_board[r][c]}"
            lines.append(row_str)
        
        return "\n".join(lines)
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get complete game state for evaluation and observation."""
        cells_revealed = 0
        cells_flagged = 0
        cells_total = self.rows * self.cols
        
        for r in range(self.rows):
            for c in range(self.cols):
                if self.display_board[r][c] not in ['X', 'F']:
                    cells_revealed += 1
                elif self.display_board[r][c] == 'F':
                    cells_flagged += 1
        
        progress = cells_revealed / max(1, cells_total - self.num_mines)
        
        return {
            "game_over": self.game_over,
            "won": self.won,
            "rows": self.rows,
            "cols": self.cols,
            "num_mines": self.num_mines,
            "cells_revealed": cells_revealed,
            "cells_flagged": cells_flagged,
            "cells_total": cells_total,
            "progress": progress,
            "board_display": self._get_board_display(),
            "mines_remaining": self.num_mines - cells_flagged
        }
    
    def get_board(self) -> Dict[str, Any]:
        """Get current board state for agent observation."""
        return {
            "board": self._get_board_display(),
            "rows": self.rows,
            "cols": self.cols,
            "mines_remaining": self.num_mines - self.mines_flagged,
            "game_over": self.game_over,
            "won": self.won
        }
