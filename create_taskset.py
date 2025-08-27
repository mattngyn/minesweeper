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
            "count": 10
        },
        # Medium tasks (7x7 board with 7 mines)
        {
            "difficulty": "medium", 
            "rows": 7,
            "cols": 7,
            "num_mines": 7,
            "count": 10
        },
        # Hard tasks (9x9 board with 10 mines - standard beginner)
        {
            "difficulty": "hard",
            "rows": 9,
            "cols": 9,
            "num_mines": 10,
            "count": 10
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
                    "random_seed": 42 + task_id  # Different seed for each task
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
                "prompt": f"Play Minesweeper on a {config['rows']}x{config['cols']} board with {config['num_mines']} mines. Try to reveal as many safe cells as possible without hitting any mines.",
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
    # Convert to HuggingFace dataset format
    dataset_dict = {
        "id": [t["id"] for t in tasks],
        "prompt": [t["prompt"] for t in tasks],
        "mcp_config": [t["mcp_config"] for t in tasks],
        "setup_tool": [t["setup_tool"] for t in tasks],
        "evaluate_tool": [t["evaluate_tool"] for t in tasks],
        "metadata": [t["metadata"] for t in tasks],
    }
    
    dataset = Dataset.from_dict(dataset_dict)
    
    # Save locally for testing
    dataset.save_to_disk("./minesweeper_taskset")
    print(f"Created {len(tasks)} minesweeper tasks")
    print("Dataset saved to ./minesweeper_taskset")
    
    # To push to HuggingFace Hub (requires authentication):
    # dataset.push_to_hub("your-username/minesweeper-taskset")
    
    # Print sample task for verification
    print("\nSample task:")
    print(json.dumps(tasks[0], indent=2))

if __name__ == "__main__":
    main()
