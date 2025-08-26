"""Minesweeper MCP server for HUD."""
from hud.server import MCPServer
from hud.server.context import attach_context
from mcp.types import TextContent
from typing import Dict, Any

mcp = MCPServer(name="minesweeper")
ctx = None

@mcp.initialize
async def init(init_ctx):
    global ctx
    ctx = attach_context("/tmp/hud_ctx.sock")

@mcp.shutdown
async def cleanup():
    global ctx
    ctx = None

@mcp.tool()
async def setup(rows: int = 9, cols: int = 9, num_mines: int = 10) -> Dict[str, Any]:
    """
    Required for HUD environments. Initialize a new minesweeper game.
    
    Args:
        rows: Number of rows on the board (default: 9)
        cols: Number of columns on the board (default: 9) 
        num_mines: Number of mines to place (default: 10)
    
    Returns:
        Game setup status and initial board state
    """
    try:
        result = ctx.new_game(rows, cols, num_mines)
        return {
            "status": "ready",
            "message": f"New {rows}x{cols} minesweeper game created with {num_mines} mines",
            "game_info": result
        }
    except ValueError as e:
        return {
            "status": "error",
            "message": str(e)
        }

@mcp.tool()
async def reveal(row: int, col: int) -> list[TextContent]:
    """
    Reveal a cell on the minesweeper board.
    
    Args:
        row: Row coordinate (0-based)
        col: Column coordinate (0-based)
    
    Returns:
        Result of the reveal action and updated board state
    """
    result = ctx.reveal_cell(row, col)
    
    # Format response for agent
    if result["status"] == "mine_hit":
        message = f"💥 GAME OVER! You hit a mine at ({row}, {col})\n\n{result['board']}"
    elif result["status"] == "won":
        message = f"🎉 CONGRATULATIONS! You won!\n\n{result['board']}"
    elif result["status"] == "revealed":
        message = f"Revealed cell ({row}, {col})\n\n{result['board']}"
    else:
        message = f"Error: {result['message']}"
    
    return [TextContent(text=message, type="text")]

@mcp.tool()
async def flag(row: int, col: int) -> list[TextContent]:
    """
    Flag or unflag a cell on the minesweeper board.
    
    Args:
        row: Row coordinate (0-based)
        col: Column coordinate (0-based)
    
    Returns:
        Result of the flag action and updated board state
    """
    result = ctx.flag_cell(row, col)
    
    if result["status"] == "flagged":
        message = f"{result['message']}\nMines remaining: {result.get('mines_flagged', 'unknown')}\n\n{result['board']}"
    else:
        message = f"Error: {result['message']}"
    
    return [TextContent(text=message, type="text")]

@mcp.tool()
async def get_board() -> list[TextContent]:
    """
    Get the current state of the minesweeper board.
    
    Returns:
        Current board display with game status information
    """
    board_state = ctx.get_board_state()
    
    status_info = []
    if board_state["game_over"]:
        if board_state["won"]:
            status_info.append("🎉 GAME WON!")
        else:
            status_info.append("💥 GAME OVER!")
    else:
        status_info.append("🎮 GAME IN PROGRESS")
    
    status_info.append(f"Mines remaining: {board_state['mines_remaining']}")
    
    message = "\n".join(status_info) + f"\n\n{board_state['board']}"
    
    return [TextContent(text=message, type="text")]

@mcp.tool()
async def evaluate() -> Dict[str, Any]:
    """
    Required for HUD environments. Return current game state for evaluation.
    
    Returns:
        Dictionary with game performance metrics
    """
    state = ctx.get_game_state()
    
    # Calculate reward based on game outcome and progress
    if state["won"]:
        reward = 1.0  # Full reward for winning
    elif state["game_over"]:
        reward = 0.0  # No reward for hitting mine
    else:
        # Partial reward based on safe progress
        reward = min(0.9, state["progress"] * 0.5)  # Cap at 0.9 to incentivize winning
    
    return {
        "reward": reward,
        "done": state["game_over"],
        "won": state["won"],
        "progress": state["progress"],
        "cells_revealed": state["cells_revealed"],
        "games_played": state["games_played"],
        "games_won": state["games_won"],
        "win_rate": state["win_rate"],
        "info": {
            "board_size": f"{state['rows']}x{state['cols']}",
            "num_mines": state["num_mines"],
            "cells_total": state["cells_total"],
            "cells_flagged": state["cells_flagged"]
        }
    }

if __name__ == "__main__":
    mcp.run()
