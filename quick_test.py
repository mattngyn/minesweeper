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
        prompt="Play minesweeper and try to win!",
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
        agent = ClaudeAgent()
        result = await agent.run(task, max_steps=30)
        
        print(f"\n🏆 Results:")
        print(f"   Won: {'✅' if result.info.get('won') else '❌'}")
        print(f"   Reward: {result.reward:.2f}")
        print(f"   Progress: {result.info.get('progress', 0):.1%}")
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
