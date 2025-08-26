#!/usr/bin/env python3
"""
Quick test to verify reward calculation is working correctly.
"""

# Test the reward calculation logic
def test_reward_calculation():
    print("🧪 Testing Reward Calculation Logic")
    print("=" * 50)
    
    # Test case 1: 6x6 board with 6 mines
    total_cells = 36
    num_mines = 6
    expected_random = (total_cells - num_mines) / (num_mines + 1)
    
    print(f"\n📋 Board: 6x6 with 6 mines")
    print(f"   Expected random: {expected_random:.2f} cells")
    
    # Test different scenarios
    test_cases = [
        (0, False, "0 cells revealed (start)"),
        (4, False, "4 cells revealed (below random)"),
        (5, False, "5 cells revealed (just above random)"),
        (15, False, "15 cells revealed (good progress)"),
        (25, False, "25 cells revealed (near win)"),
        (30, True, "30 cells revealed (won!)"),
    ]
    
    for cells_revealed, won, description in test_cases:
        if won:
            reward = 1.0
        elif cells_revealed <= expected_random:
            reward = 0.0
        else:
            max_possible = total_cells - num_mines
            cells_above_expected = cells_revealed - expected_random
            max_above_expected = max_possible - expected_random
            reward = 0.5 * (cells_above_expected / max_above_expected)
        
        print(f"   {description}: reward = {reward:.3f}")

if __name__ == "__main__":
    test_reward_calculation()
