"""Minesweeper MCP server for HUD."""
from hud.server import MCPServer
from hud.server.context import attach_context
from mcp.types import TextContent
from typing import Dict, Any
import random
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
async def setup(rows: int = 9, cols: int = 9, num_mines: int = 10, random_seed: int = 42) -> list[TextContent]:
    """
    Required for HUD environments. Initialize a new minesweeper game.
    
    Args:
        rows: Number of rows on the board (default: 9)
        cols: Number of columns on the board (default: 9) 
        num_mines: Number of mines to place (default: 10)
    
    Returns:
        Game setup status and initial board state
    """
    random.seed(random_seed)

    result = ctx.new_game(rows, cols, num_mines)
    board_state = ctx.get_board_state()
    message = f"New {rows}x{cols} minesweeper game created with {num_mines} mines\n"
    message += f"Game info: {result}\n"
    message += f"Initial board:\n{board_state['board']}"
    return [TextContent(text=message, type="text")]

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
    elif result["status"] == "already_revealed":
        message = f"Cell ({row}, {col}) is already revealed\n\n{result['board']}"
    else:
        message = f"Error: {result['message']}"
    
    message += "\n[ASCII]"
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
    
    message += "\n[ASCII]"
    
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
    status_info.append(f"\n[ASCII]")

    message = "\n".join(status_info) + f"\n\n{board_state['board']}"
    
    return [TextContent(text=message, type="text")]

@mcp.tool()
async def evaluate() -> list[TextContent]:
    """
    Required for HUD environments. Return current game state for evaluation.
    
    Returns:
        Dictionary with game performance metrics
    """
    state = ctx.get_game_state()
    
    # Calculate expected cells revealed by random play
    # Using negative hypergeometric distribution expectation: E[X] = (N - M) / (M + 1)
    # where N = total cells, M = mines
    total_cells = state["cells_total"]
    num_mines = state["num_mines"]
    expected_random_cells = (total_cells - num_mines) / (num_mines + 1)
    
    # Calculate reward based on performance vs random baseline
    cells_revealed = state["cells_revealed"]
    
    if state["won"]:
        reward = 1.0  # Full reward for winning
    else:
        reward = 0.0  # No reward for hitting a mine
    
    # Create evaluation summary for content field
    eval_summary = f"""Game Statistics:
- Cells Revealed: {cells_revealed} / {total_cells - num_mines}
- Expected Random: {expected_random_cells:.1f} cells
- Performance: {max(0, cells_revealed - expected_random_cells):.0f} cells above random
- Win Status: {'Won' if state['won'] else 'Lost'}
- Reward: {reward:.3f}"""
    
    return {
        "reward": reward,
        "content": eval_summary
    }

if __name__ == "__main__":
    mcp.run()
