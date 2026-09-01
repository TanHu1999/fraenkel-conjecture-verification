#!/usr/bin/env python3
"""Pure-Python independent audit of the finite s=1 branch verifier.

No NumPy operations, bit-mask row code, or implementation helpers are shared
with the production certificate.  The backward 0/1 DP uses Python integers.
Small moduli are also checked by literal subset enumeration.
"""

from __future__ import annotations

from itertools import combinations
from math import gcd


SCALE = 100_000_000


def vertices(q: int) -> tuple[int, ...]:
    return tuple(a for a in range(1, q) if 3 * a < q and gcd(a, q) == 1)


def kernel_ceiling(a: int, b: int, q: int) -> int:
    residue = a * pow(b, -1, q) % q
    d = min(residue, q - residue)
    numerator = SCALE * (7 * q * q + 16 * d * d)
    denominator = 7 * q * q * d
    whole, remainder = divmod(numerator, denominator)
    return whole + int(remainder != 0)


def make_weights(q: int, pool: tuple[int, ...]) -> dict[tuple[int, int], int]:
    return {
        (a, b): kernel_ceiling(a, b, q)
        for a in pool
        for b in pool
        if a != b
    }


def backward_knapsack_row(
    row: int,
    selected: frozenset[int],
    available: frozenset[int],
    q: int,
    weights: dict[tuple[int, int], int],
) -> int:
    required = selected | {row}
    capacity = q - sum(required)
    if capacity < 0:
        return -1
    starting_mass = sum(weights[row, b] for b in required if b != row)
    if starting_mass >= SCALE:
        return starting_mass
    dp = [-1] * (capacity + 1)
    dp[0] = starting_mass
    for b in sorted(available - required):
        if b > capacity:
            continue
        gain = weights[row, b]
        for used in range(capacity, b - 1, -1):
            before = dp[used - b]
            if before >= 0 and before + gain > dp[used]:
                dp[used] = before + gain
    return max(dp)


def pure_tree(q: int) -> tuple[bool, int]:
    pool = vertices(q)
    weights = make_weights(q, pool)
    nodes = 0

    def visit(selected: frozenset[int], available: frozenset[int]) -> bool:
        nonlocal nodes
        nodes += 1
        while True:
            if sum(selected) > q:
                return False
            for a in selected:
                if backward_knapsack_row(a, selected, available, q, weights) < SCALE:
                    return False
            optional = available - selected
            scores = {
                a: backward_knapsack_row(a, selected, available, q, weights)
                for a in optional
            }
            impossible = frozenset(a for a, score in scores.items() if score < SCALE)
            if not impossible:
                break
            available = available - impossible

        # This terminal is safe: when optional is empty, available=selected,
        # and every selected row was just checked with no unassigned help.
        optional = available - selected
        if not optional:
            return True
        pivot = min(optional, key=lambda a: (scores[a], a))
        return visit(selected | {pivot}, available) or visit(
            selected,
            available - {pivot},
        )

    return visit(frozenset({1}), frozenset(pool)), nodes


def literal_subset_search(q: int) -> list[int] | None:
    pool = vertices(q)
    weights = make_weights(q, pool)
    tail = pool[1:]
    for count in range(len(tail) + 1):
        for choice in combinations(tail, count):
            selected = (1,) + choice
            if sum(selected) > q:
                continue
            if all(
                sum(weights[a, b] for b in selected if b != a) >= SCALE
                for a in selected
            ):
                return list(selected)
    return None


def main() -> None:
    # Literal enumeration directly audits doom/branch completeness and the
    # terminal True condition for every Q where the candidate sets are small.
    for q in range(4, 51):
        witness = literal_subset_search(q)
        feasible, _ = pure_tree(q)
        assert feasible == (witness is not None), (q, feasible, witness)
        assert witness is None, (q, witness)

    # Pure-Python backward DP on all production hard cases plus a deterministic
    # spread across the remaining interval.
    hard = {37, 41, 43, 59, 61, 73, 91, 167}
    sample = sorted(hard | set(range(53, 716, 17)) | {289, 560, 703, 715})
    results = []
    for q in sample:
        feasible, nodes = pure_tree(q)
        assert not feasible, (q, nodes)
        results.append((q, nodes))

    print("pure-Python audit passed")
    print("literal exhaustive Q range: 4..50")
    print("backward-DP sample count:", len(sample))
    print("backward-DP maximum Q:", max(sample))
    print("sample maximum nodes:", max(results, key=lambda item: item[1]))


if __name__ == "__main__":
    main()
