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

## Learn More

- [HUD Documentation](https://docs.hud.so)
- [MCP Specification](https://modelcontextprotocol.io)
