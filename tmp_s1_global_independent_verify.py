#!/usr/bin/env python3
"""Independent finite verifier for the full s=1 problem through Q=715.

This deliberately branches on membership of 2 and 3 before any peeling.  It
uses only the global hypotheses: 1 is selected, every selected numerator is a
unit below Q/3, and the selected numerator sum is at most Q.
"""

from __future__ import annotations

from itertools import product
from math import gcd

import numpy as np


LIMIT = 715
UNIT = 100_000_000
BOTTOM = np.int64(-(1 << 61))


def delta(a: int, b: int, modulus: int) -> int:
    inverse = pow(b, -1, modulus)
    residue = a * inverse % modulus
    return residue if residue <= modulus // 2 else modulus - residue


def ceiling_weight(distance: int, modulus: int) -> int:
    """ceil(UNIT*(1/d+16d/(7Q^2))) with no division rounding down."""
    divisor = 7 * modulus * modulus * distance
    dividend = UNIT * (7 * modulus * modulus + 16 * distance * distance)
    quotient, remainder = divmod(dividend, divisor)
    return quotient + (remainder != 0)


def candidates(modulus: int) -> list[int]:
    return [
        a
        for a in range(1, modulus // 3 + 1)
        if 3 * a < modulus and gcd(a, modulus) == 1
    ]


def maximize_selected_row(
    row: int,
    live: tuple[int, ...],
    compulsory: frozenset[int],
    modulus: int,
) -> int:
    """Largest rounded row mass over all budget-feasible supersets.

    The hypothetical set is required to contain ``compulsory`` and ``row``.
    """
    required = compulsory | {row}
    if not required.issubset(live):
        return -1
    spent = sum(required)
    if spent > modulus:
        return -1
    room = modulus - spent
    initial = sum(
        ceiling_weight(delta(row, b, modulus), modulus)
        for b in required
        if b != row
    )
    best = np.full(room + 1, BOTTOM, dtype=np.int64)
    best[0] = np.int64(initial)
    for b in live:
        if b in required or b > room:
            continue
        gain = np.int64(ceiling_weight(delta(row, b, modulus), modulus))
        source = best[: room + 1 - b]
        proposal = np.where(source == BOTTOM, BOTTOM, source + gain)
        best[b:] = np.maximum(best[b:], proposal)
    return int(best.max())


def peel_branch(
    modulus: int,
    compulsory: frozenset[int],
    forbidden: frozenset[int],
) -> tuple[bool, tuple[int, ...], int]:
    live = tuple(a for a in candidates(modulus) if a not in forbidden)
    if not compulsory.issubset(live):
        return False, live, 0
    rounds = 0
    while True:
        rounds += 1
        # A compulsory failure closes the branch immediately.
        for a in sorted(compulsory):
            if maximize_selected_row(a, live, compulsory, modulus) < UNIT:
                return False, live, rounds
        rejected = []
        for a in live:
            if a in compulsory:
                continue
            if maximize_selected_row(a, live, compulsory, modulus) < UNIT:
                rejected.append(a)
        if not rejected:
            return True, live, rounds
        rejected_set = set(rejected)
        live = tuple(a for a in live if a not in rejected_set)


def membership_branches(modulus: int):
    pool = set(candidates(modulus))
    switches = [a for a in (2, 3) if a in pool]
    for flags in product((False, True), repeat=len(switches)):
        compulsory = {1}
        forbidden = set()
        for a, selected in zip(switches, flags):
            (compulsory if selected else forbidden).add(a)
        yield frozenset(compulsory), frozenset(forbidden)


def exhaustive_outer_branch(
    modulus: int,
    compulsory: frozenset[int],
    forbidden: frozenset[int],
) -> tuple[list[int] | None, int]:
    """Complete include/exclude tree, with peeling at every node."""
    node_count = 0

    def visit(
        selected: frozenset[int],
        rejected: frozenset[int],
    ) -> list[int] | None:
        nonlocal node_count
        node_count += 1
        survives, core, _ = peel_branch(modulus, selected, rejected)
        if not survives:
            return None
        optional = [a for a in core if a not in selected]
        if not optional:
            return sorted(selected)

        # Heuristic only: branch on the optional vertex having the weakest
        # possible own row once it is made compulsory.  Both children are
        # always visited unless the first yields an outer solution.
        pivot = min(
            optional,
            key=lambda a: maximize_selected_row(
                a,
                core,
                selected | {a},
                modulus,
            ),
        )
        answer = visit(selected | {pivot}, rejected)
        if answer is not None:
            return answer
        return visit(selected, rejected | {pivot})

    return visit(compulsory, forbidden), node_count


def main() -> None:
    branches = 0
    residual = []
    initial_stable = 0
    maximum_rounds = (0, None)
    maximum_tree = (0, None)
    for modulus in range(4, LIMIT + 1):
        for compulsory, forbidden in membership_branches(modulus):
            branches += 1
            survives, core, rounds = peel_branch(modulus, compulsory, forbidden)
            if rounds > maximum_rounds[0]:
                maximum_rounds = (rounds, (modulus, compulsory, forbidden))
            if survives:
                initial_stable += 1
                answer, tree_nodes = exhaustive_outer_branch(
                    modulus,
                    compulsory,
                    forbidden,
                )
                if tree_nodes > maximum_tree[0]:
                    maximum_tree = (
                        tree_nodes,
                        (modulus, compulsory, forbidden),
                    )
                if answer is not None:
                    residual.append((modulus, compulsory, forbidden, answer))
    print("Q range", 4, LIMIT)
    print("membership branches", branches)
    print("initial stable branches", initial_stable)
    print("final outer residual", len(residual))
    print("maximum rounds", maximum_rounds)
    print("maximum branch tree", maximum_tree)
    for record in residual:
        print("RESIDUAL", record)
    assert branches == 1_774
    assert initial_stable == 8
    assert not residual
    assert maximum_rounds == (
        7,
        (193, frozenset({1, 2, 3}), frozenset()),
    )
    assert maximum_tree == (
        7,
        (43, frozenset({1, 2, 3}), frozenset()),
    )


if __name__ == "__main__":
    main()
