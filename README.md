# minesweeper

A minimal HUD environment created with `hud init`.

## Quick Start

```bash
# Build and run locally
hud dev

# Or build first
docker build -t minesweeper:dev .
hud dev --image minesweeper:dev
```

## Structure

- `src/hud_controller/server.py` - MCP server with tools
- `src/hud_controller/context.py` - Persistent state across hot-reloads
- `Dockerfile` - Container configuration
- `pyproject.toml` - Python dependencies

## Adding Tools

Add new tools to `server.py`:

```python
@mcp.tool()
async def my_tool(param: str) -> str:
    """Tool description."""
    return f"Result: {param}"
```

## Adding State

Extend the `Context` class in `context.py`:

```python
class Context:
    def __init__(self):
        self.count = 0
        self.data = {}  # Add your state
```

## 🎯 Reward Function

The environment uses a sophisticated reward function that encourages strategic play:

- **Random Baseline**: Calculates expected cells revealed by random play using `E[X] = (N-M)/(M+1)`
- **No Reward for Random**: Performance at or below random level gets 0 reward
- **Strategic Play Rewarded**: Performance above random scales linearly from 0 to 0.5
- **Win Bonus**: Only winning the game achieves the full 1.0 reward
- **No Loss Penalty**: Hitting a mine ends the game but doesn't reduce earned reward

Example (6x6 board, 6 mines):
- Random play expects ~4.3 cells
- Revealing ≤4 cells = 0 reward
- Revealing 15 cells = ~0.208 reward  
- Winning (30 cells) = 1.0 reward

Run `python reward_demo.py` to see detailed examples!

## 🧪 Testing with Agents

Run `python quick_test.py` to test your environment with Claude. The evaluation summary shows:
- Cells revealed vs expected random baseline
- Performance above random play
- Final reward calculation

The HUD framework only passes `reward` and `content` fields from the evaluate tool to the agent result.

## Learn More

- [HUD Documentation](https://docs.hud.so)
- [MCP Specification](https://modelcontextprotocol.io)
