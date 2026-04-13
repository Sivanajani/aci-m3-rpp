"""
chromosome.py — Path representation for the Genetic Algorithm.

A chromosome encodes a path as a fixed list of N_WAYPOINTS intermediate
(row, col) grid cells.  The complete path is:

    START → wp[0] → wp[1] → … → wp[N-1] → GOAL

Segments between consecutive waypoints are treated as straight lines
(evaluated with Bresenham's algorithm in fitness.py).

Genetic operators provided:
    crossover(other)   — two-point crossover
    mutate(rate)       — per-gene random replacement
    apply_rdi()        — Random Domain Inversion (RDIGA only)
"""

import numpy as np
from grid import GRID_SIZE, START, GOAL

N_WAYPOINTS = 20   # number of intermediate waypoints per chromosome


class Chromosome:

    def __init__(self, waypoints=None):
        if waypoints is None:
            # Random initialisation: each waypoint is a random grid cell
            self.waypoints = [
                (np.random.randint(0, GRID_SIZE), np.random.randint(0, GRID_SIZE))
                for _ in range(N_WAYPOINTS)
            ]
        else:
            self.waypoints = list(waypoints)

    # ------------------------------------------------------------------
    def get_full_path(self):
        """Return the complete path including START and GOAL."""
        return [START] + self.waypoints + [GOAL]

    # ------------------------------------------------------------------
    def crossover(self, other, crossover_rate=0.5):
        """
        Two-point crossover.
        With probability = crossover_rate the segment [i, j) is swapped;
        otherwise both parents are returned unchanged.
        Returns a tuple (child1, child2).
        """
        if np.random.random() > crossover_rate:
            # No crossover — clone both parents
            return Chromosome(self.waypoints[:]), Chromosome(other.waypoints[:])

        n = N_WAYPOINTS
        pts = sorted(np.random.choice(n, 2, replace=False))
        i, j = pts[0], pts[1]

        child1_wps = self.waypoints[:i] + other.waypoints[i:j] + self.waypoints[j:]
        child2_wps = other.waypoints[:i] + self.waypoints[i:j] + other.waypoints[j:]

        return Chromosome(child1_wps), Chromosome(child2_wps)

    # ------------------------------------------------------------------
    def mutate(self, mutation_rate):
        """
        Per-gene mutation: each waypoint is replaced by a random grid cell
        with probability = mutation_rate.
        Returns a new Chromosome (original is unchanged).
        """
        new_wps = []
        for (r, c) in self.waypoints:
            if np.random.random() < mutation_rate:
                r = np.random.randint(0, GRID_SIZE)
                c = np.random.randint(0, GRID_SIZE)
            new_wps.append((r, c))
        return Chromosome(new_wps)

    # ------------------------------------------------------------------
    def apply_rdi(self):
        """
        Random Domain Inversion (RDI) operator — used by RDIGA only.

        Selects two random indices i ≤ j and reverses the sub-sequence
        waypoints[i : j+1].  This diversifies the search without
        discarding genetic material.
        Returns a new Chromosome.
        """
        n = N_WAYPOINTS
        pts = sorted(np.random.choice(n, 2, replace=False))
        i, j = pts[0], pts[1]

        new_wps = (
            self.waypoints[:i]
            + self.waypoints[i : j + 1][::-1]
            + self.waypoints[j + 1 :]
        )
        return Chromosome(new_wps)
