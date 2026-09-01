#!/usr/bin/env python3
"""Exact finite certificate for the s>1 near-equality branch of (SC).

The analytic reduction proved in the companion note shows that any
counterexample with minimum numerator s>1 must satisfy

    7 <= Q <= 301.

This script eliminates that finite box by monotone core peeling.  It never
evaluates a trigonometric function or a floating-point number.  For

    K_Q(d) = sin(pi/Q) / sin(pi*d/Q)

we use the strict rational envelope

    K_Q(d) < 1/d + 16*d/(7*Q**2).

Every rational weight is rounded *up* to an integer multiple of 1/SCALE.
For each current vertex a, an exact 0/1 knapsack computes the largest possible
rounded row mass among subsets with total numerator at most Q.  If that upper
bound is below SCALE, no all-pass subset can contain a, so deleting a is safe.
Iterating this deletion cannot remove a vertex belonging to a genuine
counterexample.  Thus deleting the prescribed minimum s certifies that no
counterexample with that (Q,s) exists.
"""

from __future__ import annotations

from math import gcd

import numpy as np


Q_MIN = 7
Q_MAX = 301
SCALE = 10_000_000
NEG_INF = np.int64(-(1 << 60))


def modular_distance(a: int, b: int, q: int) -> int:
    """Return ||a*b^{-1}||_q in {1,...,(q-1)/2}."""
    residue = a * pow(b, -1, q) % q
    return min(residue, q - residue)


def rounded_kernel_upper(d: int, q: int) -> int:
    """Ceiling of SCALE*(1/d + 16*d/(7*q^2)), using integers only."""
    denominator = 7 * q * q * d
    numerator = SCALE * (7 * q * q + 16 * d * d)
    return (numerator + denominator - 1) // denominator


def knapsack_row_upper(a: int, pool: list[int], q: int) -> int:
    """Exact maximum rounded row mass under sum(other numerators) <= q-a."""
    capacity = q - a
    dp = np.full(capacity + 1, NEG_INF, dtype=np.int64)
    dp[0] = 0

    for b in pool:
        if b == a or b > capacity:
            continue
        value = np.int64(rounded_kernel_upper(modular_distance(a, b, q), q))
        # Materialize the previous DP layer before updating ``dp``.  NumPy's
        # expression evaluation already makes ``candidate`` independent, but
        # the explicit copy makes the 0/1 (rather than unbounded) semantics
        # transparent to a code reviewer.
        previous = dp[:-b].copy()
        candidate = np.where(previous == NEG_INF, NEG_INF, previous + value)
        dp[b:] = np.maximum(dp[b:], candidate)

    return int(dp.max())


def peel_pair(q: int, s: int) -> tuple[int, bool, tuple[int, int, int, int, int] | None]:
    """Peel one (Q,s) pool until s is deleted or a stable core remains."""
    pool = [a for a in range(s, (q - 1) // 3 + 1) if 3 * a < q and gcd(a, q) == 1]
    if not pool or pool[0] != s:
        return 0, False, None

    removals = 0
    round_number = 0
    s_record: tuple[int, int, int, int, int] | None = None

    while pool:
        round_number += 1
        snapshot = pool[:]
        doomed: list[tuple[int, int]] = []
        for a in snapshot:
            score = knapsack_row_upper(a, snapshot, q)
            if score < SCALE:
                doomed.append((a, score))

        if not doomed:
            return removals, True, None

        doomed_set = {a for a, _ in doomed}
        for a, score in doomed:
            if a == s and s_record is None:
                s_record = (q, s, len(snapshot), round_number, score)
        removals += len(doomed)
        pool = [a for a in snapshot if a not in doomed_set]

        # Once the prescribed minimum is deleted, this (Q,s) case is
        # certified.  Deleting unrelated vertices afterwards is unnecessary.
        if s_record is not None:
            return removals, False, s_record

    raise AssertionError("peeling exhausted the pool without recording s")


def main() -> None:
    pair_count = 0
    total_removals = 0
    stable_survivors: list[tuple[int, int, list[int]]] = []
    minimum_margin = SCALE
    minimum_record: tuple[int, int, int, int, int] | None = None

    for q in range(Q_MIN, Q_MAX + 1):
        for s in range(2, (q - 1) // 3 + 1):
            if not (3 * s < q and gcd(s, q) == 1):
                continue
            pair_count += 1
            removals, has_stable_core, record = peel_pair(q, s)
            total_removals += removals
            if has_stable_core:
                stable_survivors.append((q, s, []))
            if record is None:
                raise AssertionError(f"minimum s was not deleted for Q={q}, s={s}")
            margin = SCALE - record[-1]
            if margin < minimum_margin:
                minimum_margin = margin
                minimum_record = record

    assert pair_count == 8_916, pair_count
    assert total_removals == 182_653, total_removals
    assert not stable_survivors, stable_survivors
    assert minimum_margin == 7_908, minimum_margin
    assert minimum_record == (97, 7, 26, 1, 9_992_092), minimum_record

    print("certificate passed")
    print(f"Q range: {Q_MIN}..{Q_MAX}")
    print(f"(Q,s) pairs: {pair_count}")
    print(f"removed vertices: {total_removals}")
    print("stable survivors: 0")
    print(
        "minimum s-removal margin: "
        f"{minimum_margin}/{SCALE} at "
        f"Q={minimum_record[0]}, s={minimum_record[1]}, "
        f"pool={minimum_record[2]}, round={minimum_record[3]}"
    )


if __name__ == "__main__":
    main()
