#!/usr/bin/env python3
"""Exact branch-and-knapsack certificate for the finite s=1 SC box.

For each 4 <= Q <= 715, let P be all units a with 3a<Q.  A hypothetical
all-pass set is represented by binary variables x_a, with x_1=1 and
sum(a*x_a)<=Q.  The sharp kernel envelope gives the necessary integer
row constraints

    sum_{b != a} v[a,b] x_b >= SCALE*x_a,

where v[a,b] is an upward integer rounding of
SCALE*(1/d + 16d/(7Q^2)).  The verifier exhausts these constraints using
only exact integer arithmetic.  At every node, a 0/1 knapsack computes an
upper bound for each row; impossible optional vertices are deleted, and a
stable node is split into include/exclude children.
"""

from __future__ import annotations

from collections import Counter
from math import gcd

import numpy as np


Q_MIN = 4
Q_MAX = 715
SCALE = 10_000_000
NEG = np.int64(-(1 << 60))

EXPECTED_CASES = 712
EXPECTED_NODE_HISTOGRAM = {1: 704, 3: 3, 5: 4, 7: 1}
EXPECTED_MAX_NODES = 7
EXPECTED_MAX_NODE_Q = 43


def distance(a: int, b: int, q: int) -> int:
    residue = a * pow(b, -1, q) % q
    return min(residue, q - residue)


def rounded_kernel_upper(d: int, q: int) -> int:
    denominator = 7 * q * q * d
    numerator = SCALE * (7 * q * q + 16 * d * d)
    return (numerator + denominator - 1) // denominator


def numerators(q: int) -> list[int]:
    return [
        a
        for a in range(1, (q - 1) // 3 + 1)
        if 3 * a < q and gcd(a, q) == 1
    ]


def prove_q(q: int) -> tuple[bool, int, int]:
    pool = numerators(q)
    size = len(pool)
    assert pool and pool[0] == 1

    values = np.zeros((size, size), dtype=np.int64)
    for i, a in enumerate(pool):
        for j, b in enumerate(pool):
            if i != j:
                values[i, j] = rounded_kernel_upper(distance(a, b, q), q)

    nodes = 0
    weight_cache: dict[int, int] = {}

    def bit_indices(mask: int):
        while mask:
            low_bit = mask & -mask
            yield low_bit.bit_length() - 1
            mask -= low_bit

    def weight(mask: int) -> int:
        if mask not in weight_cache:
            weight_cache[mask] = sum(pool[j] for j in bit_indices(mask))
        return weight_cache[mask]

    def row_upper(i: int, included: int, excluded: int) -> int:
        mandatory = included | (1 << i)
        capacity = q - weight(mandatory)
        if capacity < 0:
            return -1

        base = sum(
            int(values[i, j]) for j in bit_indices(mandatory) if j != i
        )

        dp = np.full(capacity + 1, NEG, dtype=np.int64)
        dp[0] = np.int64(base)
        for j, b in enumerate(pool):
            if (mandatory | excluded) >> j & 1 or b > capacity:
                continue
            # Freeze the previous layer before the in-place update so the
            # 0/1-knapsack semantics are explicit.
            old = dp[:-b].copy()
            candidate = np.where(old == NEG, NEG, old + values[i, j])
            dp[b:] = np.maximum(dp[b:], candidate)
        return int(dp.max())

    def recurse(included: int, excluded: int) -> bool:
        nonlocal nodes
        nodes += 1

        while True:
            if weight(included) > q:
                return False
            for i in bit_indices(included):
                if row_upper(i, included, excluded) < SCALE:
                    return False

            scores = [
                (row_upper(i, included, excluded), i)
                for i in range(size)
                if not (included | excluded) >> i & 1
            ]
            doomed = [i for score, i in scores if score < SCALE]
            if not doomed:
                break
            for i in doomed:
                excluded |= 1 << i

        if not scores:
            return True

        branch = min(
            (score, i)
            for score, i in scores
            if not (included | excluded) >> i & 1
        )[1]
        return recurse(included | (1 << branch), excluded) or recurse(
            included, excluded | (1 << branch)
        )

    feasible = recurse(1, 0)
    return feasible, nodes, size


def main() -> None:
    node_histogram: Counter[int] = Counter()
    max_nodes = -1
    max_node_q = -1
    cases = 0

    for q in range(Q_MIN, Q_MAX + 1):
        feasible, nodes, _ = prove_q(q)
        assert not feasible, f"unexpected feasible upper-envelope system at Q={q}"
        cases += 1
        node_histogram[nodes] += 1
        if nodes > max_nodes:
            max_nodes = nodes
            max_node_q = q

    assert cases == EXPECTED_CASES
    assert dict(sorted(node_histogram.items())) == EXPECTED_NODE_HISTOGRAM
    assert max_nodes == EXPECTED_MAX_NODES
    assert max_node_q == EXPECTED_MAX_NODE_Q

    print("certificate passed")
    print(f"Q range: {Q_MIN}..{Q_MAX}")
    print(f"Q cases: {cases}")
    print("feasible upper-envelope systems: 0")
    print(f"proof-tree node histogram: {dict(sorted(node_histogram.items()))}")
    print(f"maximum proof-tree nodes: {max_nodes} at Q={max_node_q}")
    print(f"integer scale: {SCALE}")


if __name__ == "__main__":
    main()
