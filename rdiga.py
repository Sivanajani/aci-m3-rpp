"""
rdiga.py — Random Domain Inversion Genetic Algorithm (RDIGA).

RDIGA is identical to CGA with one addition: after the mutation step,
the RDI (Random Domain Inversion) operator is applied to each offspring.

RDI operator:
    1. Select two random indices i ≤ j in the chromosome's waypoint list.
    2. Reverse the sub-sequence waypoints[i : j+1].

This reversal diversifies the population without discarding gene material,
helping the algorithm escape local optima.

Implementation detail:
    RDIGA simply inherits CGA with use_rdi=True.
    The apply_rdi() call is already guarded by that flag inside CGA.run().
"""

from cga import CGA


class RDIGA(CGA):
    """
    RDIGA — CGA + Random Domain Inversion operator.
    The only difference from CGA is use_rdi=True.
    """

    def __init__(
        self,
        pop_size=55,
        crossover_rate=0.50,
        mutation_rate=0.50,
        n_generations=50,
    ):
        super().__init__(
            pop_size=pop_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            n_generations=n_generations,
            use_rdi=True,          # ← the only structural difference vs CGA
        )
