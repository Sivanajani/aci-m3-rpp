"""
grid.py — 50x50 binary occupancy grid for Robotic Path Planning.

Cells are addressed as (row, col) with (0, 0) at the top-left.
Start = (0, 0), Goal = (49, 49).
25 % of all tiles are randomly placed as obstacles (= 625 tiles).
"""

import numpy as np

GRID_SIZE       = 50
OBSTACLE_DENSITY = 0.25          # 25 %: 625 obstacle tiles
START           = (0, 0)
GOAL            = (49, 49)


class Grid:
    """
    A 50x50 occupancy grid.
        grid[r][c] == 1  →  obstacle
        grid[r][c] == 0  →  free cell
    """

    def __init__(self):
        self.size = GRID_SIZE
        self.grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.int8)
        self._place_obstacles()
        # Pre-compute obstacle coordinates (float32) for fast proximity queries
        self.obstacle_coords = np.argwhere(self.grid == 1).astype(np.float32)

    # ------------------------------------------------------------------
    def _place_obstacles(self):
        """Place exactly 625 obstacle tiles, never on START or GOAL."""
        n = int(GRID_SIZE * GRID_SIZE * OBSTACLE_DENSITY)   # 625

        candidates = [
            (r, c)
            for r in range(GRID_SIZE)
            for c in range(GRID_SIZE)
            if (r, c) not in (START, GOAL)
        ]

        chosen_idx = np.random.choice(len(candidates), size=n, replace=False)
        for i in chosen_idx:
            r, c = candidates[i]
            self.grid[r][c] = 1

    # ------------------------------------------------------------------
    def is_obstacle(self, r, c):
        """True if (r, c) is an obstacle or lies outside the grid."""
        if r < 0 or r >= GRID_SIZE or c < 0 or c >= GRID_SIZE:
            return True
        return bool(self.grid[r][c] == 1)

    # ------------------------------------------------------------------
    def min_dist_to_obstacle(self, points: np.ndarray) -> float:
        """
        Minimum Euclidean distance from any row in *points* (shape N×2)
        to the nearest obstacle cell.
        Used by the proximity term P in the fitness function.
        """
        if len(self.obstacle_coords) == 0:
            return float("inf")

        # Vectorised broadcast: (N,1,2) − (1,M,2) → (N,M,2)
        diff = points[:, np.newaxis, :] - self.obstacle_coords[np.newaxis, :, :]
        dists = np.sqrt((diff ** 2).sum(axis=2))   # (N, M)
        return float(dists.min())
