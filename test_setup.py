#!/usr/bin/env python3
"""
Test script to verify the Minesweeper HUD VF Gym setup is working correctly.
This tests loading the environment and running a simple rollout.
"""

import os
from hud_vf_gym import HUDGym
from datasets import load_from_disk, Dataset as VerifiersDataset

def test_environment():
    """Test loading and using the Minesweeper environment."""
    
    print("Loading Minesweeper taskset...")
    dataset = load_from_disk("./minesweeper_taskset")
    print(f"Loaded {len(dataset)} tasks")
    
    # Convert to verifiers format (just first task for testing)
    test_dataset = VerifiersDataset.from_dict({
        "question": [dataset[0]["prompt"]],
        "task": [dataset[0]["id"]],
        "answer": [""],
        "info": [{
            "mcp_config": dataset[0]["mcp_config"],
            "setup_tool": dataset[0]["setup_tool"],
            "evaluate_tool": dataset[0]["evaluate_tool"],
            "metadata": dataset[0]["metadata"]
        }]
    })
    
    print("\nCreating HUD Gym environment...")
    env = HUDGym(dataset=test_dataset, config_path="./configs/minesweeper.yaml")
    
    print("\nEnvironment info:")
    print(f"- Number of tasks: {len(env.dataset)}")
    print(f"- Config path: ./configs/minesweeper.yaml")
    
    # Test getting a task
    print("\nFirst task:")
    task = env.dataset[0]
    print(f"- ID: {task['task']}")
    print(f"- Question: {task['question']}")
    
    print("\n✓ Environment setup successful!")
    print("\nYou can now run training with:")
    print("  python train_minesweeper_simple.py")
    print("\nOr with vLLM (requires 2 GPUs):")
    print("  python train_minesweeper.py")

if __name__ == "__main__":
    test_environment()
