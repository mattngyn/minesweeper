#!/usr/bin/env python3
"""
Demonstration of the new reward function for minesweeper.
Shows how rewards are calculated based on performance vs random baseline.
"""

def calculate_reward(cells_revealed, total_cells, num_mines, won=False):
    """Calculate reward using the new function."""
    # Expected cells by random play: E[X] = (N - M) / (M + 1)
    expected_random_cells = (total_cells - num_mines) / (num_mines + 1)
    
    if won:
        return 1.0, expected_random_cells
    
    if cells_revealed <= expected_random_cells:
        return 0.0, expected_random_cells
    
    # Scale from 0 to 0.5 for performance above random
    max_possible = total_cells - num_mines
    cells_above_expected = cells_revealed - expected_random_cells
    max_above_expected = max_possible - expected_random_cells
    
    reward = 0.5 * (cells_above_expected / max_above_expected)
    return reward, expected_random_cells

def demo_board_configs():
    """Show reward calculations for different board configurations."""
    print("🎮 Minesweeper Reward Function Demonstration")
    print("=" * 60)
    print()
    
    # Different board configurations
    configs = [
        (6, 6, 6),    # Easy: 36 cells, 6 mines
        (8, 8, 12),   # Medium: 64 cells, 12 mines  
        (9, 9, 16),   # Hard: 81 cells, 16 mines
        (16, 16, 40), # Expert: 256 cells, 40 mines
    ]
    
    for rows, cols, mines in configs:
        total_cells = rows * cols
        safe_cells = total_cells - mines
        
        print(f"📋 Board: {rows}x{cols} with {mines} mines")
        print(f"   Total cells: {total_cells}, Safe cells: {safe_cells}")
        
        # Calculate expected random performance
        expected_random = (total_cells - mines) / (mines + 1)
        print(f"   Expected random cells: {expected_random:.1f}")
        print()
        
        # Show rewards for different performance levels
        test_cases = [
            ("Random level", int(expected_random)),
            ("25% progress", int(safe_cells * 0.25)),
            ("50% progress", int(safe_cells * 0.5)),
            ("75% progress", int(safe_cells * 0.75)),
            ("90% progress", int(safe_cells * 0.9)),
            ("Won the game", safe_cells),
        ]
        
        print("   Performance → Reward:")
        for label, cells in test_cases:
            won = (cells == safe_cells)
            reward, _ = calculate_reward(cells, total_cells, mines, won)
            
            if cells <= expected_random and not won:
                status = "❌ No reward (≤ random)"
            elif won:
                status = "🎉 Full reward (won!)"
            else:
                cells_above = cells - expected_random
                status = f"✅ {cells_above:.0f} above random"
            
            print(f"   {label:15} ({cells:3} cells) → {reward:.3f} {status}")
        
        print()

def example_game_progression():
    """Show how reward changes during a game."""
    print("📈 Example Game Progression (8x8 board, 12 mines)")
    print("=" * 60)
    print()
    
    total_cells = 64
    mines = 12
    safe_cells = 52
    expected_random = (total_cells - mines) / (mines + 1)
    
    print(f"Expected random: {expected_random:.1f} cells")
    print(f"Need > {expected_random:.0f} cells for any reward")
    print()
    
    # Simulate a game progression
    moves = [
        (3, "Revealed corner (flood fill)"),
        (8, "Revealed another safe area"),  
        (12, "Good deduction move"),
        (18, "Cleared a difficult section"),
        (25, "Strong logical play"),
        (35, "Expert deduction"),
        (45, "Near completion"),
        (52, "Won the game!"),
    ]
    
    print("Move # | Cells | Reward | Notes")
    print("-------|-------|--------|--------------------------------")
    
    for cells, note in moves:
        won = (cells == safe_cells)
        reward, _ = calculate_reward(cells, total_cells, mines, won)
        
        if cells <= expected_random:
            reward_str = f"{reward:.3f}"
        elif won:
            reward_str = f"{reward:.3f} ⭐"
        else:
            reward_str = f"{reward:.3f}"
            
        print(f"  {cells:3}  |  {cells:3}  | {reward_str} | {note}")

if __name__ == "__main__":
    demo_board_configs()
    print("\n" + "="*60 + "\n")
    example_game_progression()
    
    print("\n💡 Key Insights:")
    print("   • Random play gets 0 reward")
    print("   • Better-than-random play scales from 0 → 0.5") 
    print("   • Only winning gets the full 1.0 reward")
    print("   • Losing doesn't penalize - you keep earned reward")
    print("   • This encourages strategic play over random clicking!")
