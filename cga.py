"""
cga.py — Conventional Genetic Algorithm (CGA) for Robotic Path Planning.

Algorithm outline per generation:
    1. Evaluate fitness for every chromosome.
    2. Keep the single best chromosome unchanged (elitism).
    3. Fill the rest of the new population:
         a. Select two parents via tournament selection (size 3).
         b. Apply two-point crossover with probability = crossover_rate.
         c. Mutate each child (per-gene probability = mutation_rate).
         [d. Apply RDI operator — RDIGA only, controlled by use_rdi flag]
    4. Replace the old population with the new one.

Parameters (matching the paper):
    pop_size       = 55
    crossover_rate = 0.50
    mutation_rate  = 0.50 or 0.80
    n_generations  = 50
"""

import time
import numpy as np

from chromosome import Chromosome
from fitness import compute_fitness, count_collisions, compute_distance

TOURNAMENT_SIZE = 3


class CGA:

    def __init__(
        self,
        pop_size=55,
        crossover_rate=0.50,
        mutation_rate=0.50,
        n_generations=50,
        use_rdi=False,          # set True by RDIGA subclass
    ):
        self.pop_size       = pop_size
        self.crossover_rate = crossover_rate
        self.mutation_rate  = mutation_rate
        self.n_generations  = n_generations
        self.use_rdi        = use_rdi

    # ------------------------------------------------------------------
    def _init_population(self):
        return [Chromosome() for _ in range(self.pop_size)]

    # ------------------------------------------------------------------
    def _evaluate(self, population, grid):
        """
        Evaluate every chromosome and return a list sorted by fitness
        (ascending — lower is better).
        Each element is a (fitness_value, chromosome) tuple.
        """
        scored = [(compute_fitness(ch, grid), ch) for ch in population]
        scored.sort(key=lambda x: x[0])
        return scored

    # ------------------------------------------------------------------
    def _tournament_select(self, scored):
        """
        Tournament selection: draw TOURNAMENT_SIZE random candidates and
        return the chromosome with the lowest fitness.
        """
        idxs = np.random.choice(len(scored), TOURNAMENT_SIZE, replace=False)
        best = min(idxs, key=lambda i: scored[i][0])
        return scored[best][1]

    # ------------------------------------------------------------------
    def run(self, grid):
        """
        Execute the GA on *grid* for n_generations generations.

        Returns
        -------
        best_fitness_per_gen : list[float]   — best fitness at each generation
        best_chromosome      : Chromosome    — overall best chromosome found
        stats                : dict          — summary metrics for this run
        """
        t_start = time.time()

        population = self._init_population()
        best_fitness_per_gen  = []
        overall_best_fitness  = float("inf")
        overall_best_chrom    = None

        for gen in range(self.n_generations):

            # ---- evaluation & bookkeeping ----------------------------
            scored = self._evaluate(population, grid)
            gen_best_fitness = scored[0][0]
            best_fitness_per_gen.append(gen_best_fitness)

            if gen_best_fitness < overall_best_fitness:
                overall_best_fitness = gen_best_fitness
                overall_best_chrom   = scored[0][1]

            # ---- build next generation --------------------------------
            # Elitism: carry the best individual forward unchanged
            next_pop = [scored[0][1]]

            while len(next_pop) < self.pop_size:
                p1 = self._tournament_select(scored)
                p2 = self._tournament_select(scored)

                # Crossover
                c1, c2 = p1.crossover(p2, self.crossover_rate)

                # Mutation
                c1 = c1.mutate(self.mutation_rate)
                c2 = c2.mutate(self.mutation_rate)

                # RDI (only active in RDIGA)
                if self.use_rdi:
                    c1 = c1.apply_rdi()
                    c2 = c2.apply_rdi()

                next_pop.append(c1)
                if len(next_pop) < self.pop_size:
                    next_pop.append(c2)

            population = next_pop

        # ---- final statistics ----------------------------------------
        elapsed   = time.time() - t_start
        best_path = overall_best_chrom.get_full_path()

        stats = {
            "best_fitness"        : overall_best_fitness,
            "path_length"         : compute_distance(best_path),
            "obstacle_collisions" : count_collisions(best_path, grid),
            "runtime_seconds"     : elapsed,
        }

        return best_fitness_per_gen, overall_best_chrom, stats
