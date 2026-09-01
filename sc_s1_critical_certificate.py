#!/usr/bin/env python3
"""Exact certificate for the critical s=1, 2-in-A, 3-not-in-A branch.

This verifies the finite part of the following reduction.  If y is the
first selected row-1-good numerator which is not a power of two, then the
good part of its reciprocal row is at most ``good_upper(q, y)`` below.
The row-1 slack estimate bounds the bad and sine-kernel corrections.  The
resulting upper bound is strictly below one for every odd q >= 290 in the
analytic box q <= 5607.

Only exact integer and Fraction arithmetic is used.
"""

from __future__ import annotations

from fractions import Fraction
from math import isqrt


Q_MIN = 7
Q_MAX = 5607
EXCLUSION_START = 290

EXPECTED_PAIRS = 39_232
EXPECTED_SURVIVORS = 155
EXPECTED_MAX_SURVIVOR_Q = 289
EXPECTED_SURVIVOR_Y = {5, 6, 7, 9, 10, 11, 12, 14, 18, 20, 24, 48, 96}
EXPECTED_MIN_MARGIN = Fraction(1_140_922_873_693, 64_523_567_545_080)
EXPECTED_MIN_CASE = (311, 24)


def divisors(n: int) -> set[int]:
    ans: set[int] = set()
    for d in range(1, isqrt(n) + 1):
        if n % d == 0:
            ans.add(d)
            ans.add(n // d)
    return ans


def distance(a: int, b: int, q: int) -> int:
    residue = a * pow(b, -1, q) % q
    return min(residue, q - residue)


def candidate_good(q: int) -> set[int]:
    """All possible row-1-good numerators in the subcritical interval."""
    return {
        a
        for a in divisors(q - 1) | divisors(q + 1)
        if 2 <= a and 3 * a < q
    }


def n_max(q: int) -> int:
    """Largest n with (n+1)(n+2)/2 <= q."""
    return (isqrt(8 * q + 1) - 3) // 2


def good_upper(q: int, y: int, good: set[int]) -> Fraction:
    """Upper bound for the good part of the y-row harmonic mass.

    Put y=2^v*m with m odd.  The predecessor sum is maximized by taking
    every dyadic divisor 1,2,...,2^v, whose numerator sum is p=2^(v+1)-1.
    All far good terms have value/cost at most 1/(y(q-1)).  We allocate the
    entire remaining numerator budget to that baseline, and then add only
    the positive promotions for the exceptional X and C terms.
    """
    two_part = y & -y
    v = two_part.bit_length() - 1
    p = (1 << (v + 1)) - 1

    upper = Fraction(p, y) + Fraction(q - y - p, y * (q - 1))

    for b in good:
        if b == y:
            continue
        in_x = b < y and (b & (b - 1) == 0) and y % b != 0
        in_c = y < b < 2 * y
        if not (in_x or in_c):
            continue

        promotion = Fraction(1, distance(y, b, q)) - Fraction(
            b, y * (q - 1)
        )
        if promotion > 0:
            upper += promotion

    return upper


def total_upper(q: int, y: int, good: set[int]) -> Fraction:
    """Good mass plus exact rational bad/kernel perturbation envelope."""
    n = n_max(q)
    return (
        good_upper(q, y, good)
        + Fraction(16 * n, 7 * (q - y))
        + Fraction(8 * n, 7 * q)
    )


def main() -> None:
    pairs = 0
    survivors: list[tuple[int, int]] = []
    min_margin: Fraction | None = None
    min_case: tuple[int, int] | None = None

    for q in range(Q_MIN, Q_MAX + 1, 2):
        good = candidate_good(q)
        for y in sorted(good):
            if y < 5 or y & (y - 1) == 0:
                continue
            pairs += 1
            bound = total_upper(q, y, good)
            if bound >= 1:
                survivors.append((q, y))
            elif q >= EXCLUSION_START:
                margin = 1 - bound
                if min_margin is None or margin < min_margin:
                    min_margin = margin
                    min_case = (q, y)

    survivor_y = {y for _, y in survivors}
    max_survivor_q = max(q for q, _ in survivors)

    assert pairs == EXPECTED_PAIRS
    assert len(survivors) == EXPECTED_SURVIVORS
    assert max_survivor_q == EXPECTED_MAX_SURVIVOR_Q
    assert survivor_y == EXPECTED_SURVIVOR_Y
    assert min_margin == EXPECTED_MIN_MARGIN
    assert min_case == EXPECTED_MIN_CASE

    print("certificate passed")
    print(f"odd Q range: {Q_MIN}..{Q_MAX}")
    print(f"eligible (Q,y) pairs: {pairs}")
    print(f"unexcluded pairs: {len(survivors)}")
    print(f"largest unexcluded Q: {max_survivor_q}")
    print(f"unexcluded y values: {sorted(survivor_y)}")
    print(f"minimum excluded margin: {min_margin}")
    print(f"minimum-margin case: Q={min_case[0]}, y={min_case[1]}")


if __name__ == "__main__":
    main()
