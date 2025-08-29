"""
Random-play Minesweeper simulator (cascades, no first-click safety).

- We repeatedly click uniformly at random among still-hidden cells
  until we click a mine or all safe cells are revealed (solved).
- We count how many SAFE cells were revealed in that run.
- We repeat for N runs and report a percentile threshold (e.g., P99).

Usage examples:
    python minesim.py
    python minesim.py --rows 5 --cols 5 --mines 3 --runs 200000 --percentile 99
    python minesim.py --rows 8 --cols 8 --mines 10 --runs 100000 --percentile 95
"""

from __future__ import annotations
import argparse
import math
import random
import statistics
from collections import deque
from typing import Iterable, List, Set, Tuple

# ---------- Core board helpers ----------

NEIGH = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

def neighbors(r: int, c: int, rows: int, cols: int) -> Iterable[Tuple[int,int]]:
    for dr, dc in NEIGH:
        rr, cc = r + dr, c + dc
        if 0 <= rr < rows and 0 <= cc < cols:
            yield rr, cc

def rc_to_idx(r: int, c: int, cols: int) -> int:
    return r * cols + c

def idx_to_rc(i: int, cols: int) -> Tuple[int,int]:
    return divmod(i, cols)

def place_mines(total: int, nmines: int, rng: random.Random) -> Set[int]:
    # Mines are freshly randomized EVERY run
    return set(rng.sample(range(total), nmines))

def build_counts(rows: int, cols: int, mines: Set[int]) -> List[int]:
    """
    Returns a flat list of length rows*cols:
      -1 for a mine, else the count of adjacent mines.
    """
    total = rows * cols
    counts = [0] * total
    for i in range(total):
        if i in mines:
            counts[i] = -1
        else:
            r, c = idx_to_rc(i, cols)
            cnt = 0
            for rr, cc in neighbors(r, c, rows, cols):
                if rc_to_idx(rr, cc, cols) in mines:
                    cnt += 1
            counts[i] = cnt
    return counts

def reveal_with_cascade(target: int, counts: List[int], rows: int, cols: int,
                        revealed: Set[int]) -> Set[int]:
    """
    Reveal a SAFE cell; if it is 0, flood-fill all connected zeros and
    their bordering numbers. Return the set of newly revealed indices.
    """
    newly = set()
    if target in revealed:
        return newly

    if counts[target] > 0:
        revealed.add(target)
        newly.add(target)
        return newly

    # Zero: BFS over zero-cells; reveal their bordering numbers too.
    q = deque([target])
    zero_seen = set()
    while q:
        cur = q.popleft()
        if cur in zero_seen:
            continue
        zero_seen.add(cur)
        if cur not in revealed:
            revealed.add(cur)
            newly.add(cur)
        r, c = idx_to_rc(cur, cols)
        for rr, cc in neighbors(r, c, rows, cols):
            j = rc_to_idx(rr, cc, cols)
            if counts[j] == 0 and j not in zero_seen:
                q.append(j)
            if counts[j] >= 0:  # safe border numbers also get revealed
                if j not in revealed:
                    revealed.add(j)
                    newly.add(j)
    return newly

# ---------- Single run & simulation ----------

def run_one(rows: int, cols: int, nmines: int, rng: random.Random) -> int:
    """
    Run one random-play game. Returns the number of SAFE cells revealed
    before the first mine click (or before solving).
    """
    total = rows * cols
    safe_total = total - nmines

    mines = place_mines(total, nmines, rng)
    counts = build_counts(rows, cols, mines)

    revealed: Set[int] = set()       # SAFE cells that have been revealed
    hidden: Set[int] = set(range(total))  # everything not yet revealed

    while True:
        # solved without hitting a mine
        if len(revealed) == safe_total:
            return len(revealed)

        # choose a random hidden cell (could be mine or safe)
        candidates = list(hidden - revealed)
        if not candidates:
            return len(revealed)
        choice = rng.choice(candidates)

        if choice in mines:
            # mine clicked → stop
            return len(revealed)
        else:
            # reveal safe (with cascade if 0)
            newly = reveal_with_cascade(choice, counts, rows, cols, revealed)
            # mark those as no longer hidden
            for j in newly:
                if j in hidden:
                    hidden.remove(j)

def simulate(rows: int, cols: int, nmines: int, runs: int, seed: int | None = None) -> List[int]:
    """
    Returns a list of 'safe cells revealed' counts for each run.
    Mines are re-sampled fresh for every run.
    """
    rng = random.Random(seed)
    return [run_one(rows, cols, nmines, rng) for _ in range(runs)]

# ---------- Percentile helper (nearest-rank, "higher") ----------

def percentile_threshold(data: List[int], percentile: float) -> int:
    """
    Nearest-rank 'higher' percentile:
    - Sort ascending, take element at ceil(p/100 * n).
    - This mirrors NumPy's method='higher' behavior for discrete data.
    """
    if not data:
        raise ValueError("Empty dataset.")
    if not (0 < percentile <= 100):
        raise ValueError("percentile must be in (0, 100].")
    xs = sorted(data)
    n = len(xs)
    rank = math.ceil(percentile / 100.0 * n)
    idx = max(0, min(n - 1, rank - 1))
    return xs[idx]

# ---------- CLI ----------

def main():
    ap = argparse.ArgumentParser(description="Random-play Minesweeper simulator (cascades, no first-click safety).")
    ap.add_argument("--rows", type=int, default=5, help="Number of rows (default: 5)")
    ap.add_argument("--cols", type=int, default=5, help="Number of cols (default: 5)")
    ap.add_argument("--mines", type=int, default=3, help="Number of mines (default: 3)")
    ap.add_argument("--runs", type=int, default=200_000, help="Number of simulated runs (default: 200000)")
    ap.add_argument("--percentile", type=float, default=99.0, help="Percentile to report, e.g. 99 for top 1%% (default: 99)")
    ap.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")
    args = ap.parse_args()

    total = args.rows * args.cols
    if args.mines <= 0 or args.mines >= total:
        raise ValueError("mines must be between 1 and rows*cols - 1")

    results = simulate(args.rows, args.cols, args.mines, args.runs, seed=args.seed)

    # summary stats
    safe_total = total - args.mines
    pval = percentile_threshold(results, args.percentile)
    mean_val = statistics.fmean(results)
    stdev_val = statistics.pstdev(results)  # population stdev

    print(f"Board: {args.rows}x{args.cols}, mines: {args.mines} (safe cells: {safe_total})")
    print(f"Runs: {args.runs}, seed: {args.seed}")
    print(f"P{args.percentile:g} threshold (safe cells revealed): {pval} (out of {safe_total})")
    print(f"Mean: {mean_val:.3f}, StdDev: {stdev_val:.3f}, Min: {min(results)}, Max: {max(results)}")

if __name__ == "__main__":
    main()
