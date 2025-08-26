#!/usr/bin/env python3
"""
Quick test script to run a Claude agent on your minesweeper environment.
Run this after building your Docker image.
"""
import asyncio
import os
import hud
from hud.datasets import Task
from hud.agents import ClaudeAgent
from hud.types import MCPToolCall

async def main():
    print("🎮 Quick Minesweeper Agent Test")
    print("Building and testing your environment...")
    
    # Simple task configuration
    task = Task(
        prompt="""Play minesweeper until you either WIN or LOSE. You MUST continue playing until the game ends.
        
        Strategy:
        1. Start by revealing cells to gather information
        2. Use logical deduction to identify mine locations
        3. Flag cells you're certain contain mines
        4. Continue revealing safe cells until you've cleared all non-mine cells (WIN) or hit a mine (LOSE)
        
        IMPORTANT: Do NOT stop playing early. Keep playing until you achieve victory or hit a mine.
        The game only ends when you've either won or lost - partial progress is not enough!""",
        mcp_config={
            "minesweeper": {
                "command": "docker",
                "args": ["run", "--rm", "-i", "minesweeper:dev"]
            }
        },
        setup_tool=MCPToolCall(name="setup", arguments={"rows": 6, "cols": 6, "num_mines": 6}),
        evaluate_tool=MCPToolCall(name="evaluate", arguments={})
    )
    
    # Run with tracing
    with hud.trace("minesweeper-quick-test"):
        agent = ClaudeAgent(model="claude-opus-4-1-20250805")
        result = await agent.run(task, max_steps=30)
        
        print(f"\n🏆 Results:")
        print(f"   Reward: {result.reward:.3f}")
        
        # Show evaluation summary from content field
        if result.content:
            print(f"\n📈 Evaluation Summary:")
            for line in result.content.split('\n'):
                if line.strip():
                    print(f"   {line}")
        
        print(f"\n📊 View full trace at: https://app.hud.so")

if __name__ == "__main__":
    # Check if docker image exists first
    import subprocess
    try:
        subprocess.run(["docker", "images", "minesweeper:dev"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ Docker image 'minesweeper:dev' not found!")
        print("   Run: docker build -t minesweeper:dev .")
        exit(1)
    
    asyncio.run(main())
