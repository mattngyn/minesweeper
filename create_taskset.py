#!/usr/bin/env python3
"""
Create a simple Minesweeper taskset for HUD VF Gym training.
This creates tasks with varying difficulty levels.
"""

import json
from datasets import Dataset
from hud.datasets import save_tasks

def create_minesweeper_tasks():
    """Create a variety of minesweeper tasks for training."""
    tasks = []
    
    # Task templates with different difficulties
    task_configs = [
        # Easy tasks (5x5 board with 3 mines)
        {
            "difficulty": "easy",
            "rows": 5,
            "cols": 5,
            "num_mines": 3,
            "count": 100
        },
        # Medium tasks (7x7 board with 7 mines)
        {
            "difficulty": "medium", 
            "rows": 7,
            "cols": 7,
            "num_mines": 7,
            "count": 0
        },
        # Hard tasks (9x9 board with 10 mines - standard beginner)
        {
            "difficulty": "hard",
            "rows": 9,
            "cols": 9,
            "num_mines": 10,
            "count": 0
        }
    ]
    
    task_id = 0
    for config in task_configs:
        for i in range(config["count"]):
            task_id += 1
            
            # Create MCP configuration - mimicking quick_test.py structure
            mcp_config = {
                "minesweeper": {
                    "command": "docker",
                    "args": ["run", "--rm", "-i", "minesweeper:dev"]
                }
            }
            
            # Setup tool to initialize the game - matching quick_test.py MCPToolCall format
            setup_tool = {
                "name": "setup",
                "arguments": {
                    "rows": config["rows"],
                    "cols": config["cols"],
                    "num_mines": config["num_mines"],
                    "random_seed": 42  # Same seed for each task
                }
            }
            
            # Evaluate tool to check performance - matching quick_test.py MCPToolCall format
            evaluate_tool = {
                "name": "evaluate",
                "arguments": {}
            }
            
            # Create the task
            task = {
                "id": f"minesweeper_{config['difficulty']}_{task_id}",
                "prompt": f"Play Minesweeper on a {config['rows']}x{config['cols']} board with {config['num_mines']} mines. Try to reveal as many safe cells as possible without hitting any mines. You must call tools one by one. Once the game is over, you must stop. If you continue to be unable to call tools, you must stop.",
                "mcp_config": json.dumps(mcp_config),
                "setup_tool": json.dumps(setup_tool),
                "evaluate_tool": json.dumps(evaluate_tool),
                "metadata": json.dumps({
                    "difficulty": config["difficulty"],
                    "board_size": f"{config['rows']}x{config['cols']}",
                    "num_mines": config["num_mines"],
                    "task_number": i + 1,
                    "answer": ""  # No specific answer for minesweeper
                })
            }
            
            tasks.append(task)
    
    return tasks

def main():
    # Create tasks
    tasks = create_minesweeper_tasks()
    
    save_tasks(tasks, "kizro/minesweeper_taskset")
    print("Pushed to HF")

    print("\nSample task:")
    print(json.dumps(tasks[0], indent=2))

if __name__ == "__main__":
    main()
