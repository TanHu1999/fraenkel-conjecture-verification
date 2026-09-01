#!/usr/bin/env python3
"""Independent pure-Python audit of the production s>1 certificate.

This is an audit helper, not a logical dependency of the manuscript.  It
shares no NumPy operations with the production verifier: every row maximum
is computed by a backward 0/1 knapsack over ordinary Python integers.
"""

from math import gcd


Q_MIN = 7
Q_MAX = 301
SCALE = 10_000_000


def distance(a: int, b: int, q: int) -> int:
    residue = a * pow(b, -1, q) % q
    return min(residue, q - residue)


def ceiling_weight(d: int, q: int) -> int:
    numerator = SCALE * (7 * q * q + 16 * d * d)
    denominator = 7 * q * q * d
    quotient, remainder = divmod(numerator, denominator)
    return quotient + int(remainder != 0)


def row_maximum(a: int, pool: tuple[int, ...], q: int) -> int:
    capacity = q - a
    dp = [-1] * (capacity + 1)
    dp[0] = 0
    for b in pool:
        if b == a or b > capacity:
            continue
        gain = ceiling_weight(distance(a, b, q), q)
        for used in range(capacity, b - 1, -1):
            previous = dp[used - b]
            if previous >= 0 and previous + gain > dp[used]:
                dp[used] = previous + gain
    return max(dp)


def peel(q: int, s: int):
    pool = tuple(
        a for a in range(s, q) if 3 * a < q and gcd(a, q) == 1
    )
    assert pool and pool[0] == s
    removals = 0
    round_number = 0
    while True:
        round_number += 1
        doomed = tuple(
            (a, row_maximum(a, pool, q))
            for a in pool
        )
        doomed = tuple((a, score) for a, score in doomed if score < SCALE)
        assert doomed, (q, s, pool)
        for a, score in doomed:
            if a == s:
                return removals + len(doomed), (
                    q,
                    s,
                    len(pool),
                    round_number,
                    score,
                )
        removals += len(doomed)
        doomed_vertices = {a for a, _ in doomed}
        pool = tuple(a for a in pool if a not in doomed_vertices)


def main() -> None:
    pairs = 0
    removals = 0
    minimum_margin = SCALE
    minimum_record = None
    for q in range(Q_MIN, Q_MAX + 1):
        for s in range(2, q):
            if not (3 * s < q and gcd(s, q) == 1):
                continue
            pairs += 1
            removed, record = peel(q, s)
            removals += removed
            margin = SCALE - record[-1]
            if margin < minimum_margin:
                minimum_margin = margin
                minimum_record = record

    assert pairs == 8_916
    assert removals == 182_653
    assert minimum_margin == 7_908
    assert minimum_record == (97, 7, 26, 1, 9_992_092)
    print("pure-Python s>1 audit passed")
    print("(Q,s) pairs:", pairs)
    print("removed vertices:", removals)
    print("minimum record:", minimum_record)


if __name__ == "__main__":
    main()
