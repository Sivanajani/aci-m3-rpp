"""
fitness.py — Fitness function for Robotic Path Planning.

Formula (minimisation):
    F = O*55  +  P*20  +  A*5  +  D*2

Components:
    O  — obstacle collisions  (hard constraint, weight 55)
         Number of grid cells along path segments that are obstacles.
    P  — proximity to obstacles (soft, weight 20)
         P = e^(−0.2 × min_distance_to_obstacle)   ∈ [0, 1]
    A  — maximum turning angle along the path (soft, weight 5)
         Angle at each intermediate waypoint, in radians.
    D  — total path length (Euclidean, soft, weight 2)

Lower fitness = better path.
"""

import math
import numpy as np


# -----------------------------------------------------------------------
# Public entry point
# -----------------------------------------------------------------------

def compute_fitness(chromosome, grid):
    """Return the scalar fitness value F for *chromosome* on *grid*."""
    path = chromosome.get_full_path()

    O = count_collisions(path, grid)
    P = compute_proximity(path, grid)
    A = compute_max_angle(path)
    D = compute_distance(path)

    return O * 55 + P * 20 + A * 5 + D * 2


# -----------------------------------------------------------------------
# Component functions (also used by experiment.py for per-run statistics)
# -----------------------------------------------------------------------

def count_collisions(path, grid):
    """
    Count how many cells along the straight-line segments of *path*
    are obstacle cells.  Uses Bresenham's line algorithm.
    """
    total = 0
    for k in range(len(path) - 1):
        r0, c0 = path[k]
        r1, c1 = path[k + 1]
        cells = _bresenham(r0, c0, r1, c1)
        if cells:
            arr = np.array(cells)                        # shape (N, 2)
            total += int(grid.grid[arr[:, 0], arr[:, 1]].sum())
    return total


def compute_proximity(path, grid):
    """
    P = e^(−0.2 × d_min)
    where d_min is the minimum Euclidean distance from any waypoint in
    *path* to the nearest obstacle cell.
    """
    path_arr = np.array(path, dtype=np.float32)          # (N, 2)
    d_min = grid.min_dist_to_obstacle(path_arr)
    return math.exp(-0.2 * d_min)


def compute_max_angle(path):
    """
    Maximum turning angle (radians) at any intermediate waypoint.
    The angle at point i is the angle between vectors (i-1 → i) and (i → i+1).
    Returns 0.0 if the path has fewer than 3 points.
    """
    if len(path) < 3:
        return 0.0

    max_angle = 0.0
    for i in range(1, len(path) - 1):
        r0, c0 = path[i - 1]
        r1, c1 = path[i]
        r2, c2 = path[i + 1]

        v1 = np.array([r1 - r0, c1 - c0], dtype=float)
        v2 = np.array([r2 - r1, c2 - c1], dtype=float)

        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)
        if n1 < 1e-9 or n2 < 1e-9:
            continue

        cos_a = np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)
        angle = math.acos(cos_a)
        if angle > max_angle:
            max_angle = angle

    return max_angle


def compute_distance(path):
    """Total Euclidean length of the path."""
    total = 0.0
    for k in range(len(path) - 1):
        r0, c0 = path[k]
        r1, c1 = path[k + 1]
        total += math.sqrt((r1 - r0) ** 2 + (c1 - c0) ** 2)
    return total


# -----------------------------------------------------------------------
# Internal helper
# -----------------------------------------------------------------------

def _bresenham(r0, c0, r1, c1):
    """
    Return all integer grid cells on the line from (r0, c0) to (r1, c1).
    Handles all octants correctly.
    """
    cells = []
    dr = abs(r1 - r0)
    dc = abs(c1 - c0)
    r, c = r0, c0
    sr = 1 if r1 > r0 else -1
    sc = 1 if c1 > c0 else -1

    if dc >= dr:                   # step along columns
        err = dc / 2.0
        while c != c1:
            cells.append((r, c))
            err -= dr
            if err < 0:
                r += sr
                err += dc
            c += sc
    else:                          # step along rows
        err = dr / 2.0
        while r != r1:
            cells.append((r, c))
            err -= dc
            if err < 0:
                c += sc
                err += dr
            r += sr

    cells.append((r1, c1))        # always include the endpoint
    return cells
