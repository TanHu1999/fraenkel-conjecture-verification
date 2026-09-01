# Fraenkel conjecture finite-case verification package


## Files in this repository

- `sc_s_gt1_near_certificate.py` — exact finite certificate for the `s>1`
  box `7 <= Q <= 301`.
- `sc_s1_critical_certificate.py` — exact rational cutoff certificate for the
  critical `s=1` branch.
- `sc_s1_finite_certificate.py` — exact branch-and-knapsack certificate for
  all `4 <= Q <= 715`.
- `tmp_s1_global_independent_verify.py` and
  `tmp_s1_pure_python_audit.py` — logically redundant independent audits
  of the `s=1` verifier.
- `tmp_s_gt1_pure_python_audit.py` — a pure-Python, backward-knapsack
  full-box audit of the `s>1` certificate.

Only the three `sc_*.py` files listed above are logical proof steps.

## Run the finite-case verification

```bash
python -I sc_s_gt1_near_certificate.py
python -I sc_s1_critical_certificate.py
python -I sc_s1_finite_certificate.py
```

The three runs must end with `certificate passed`.  The reference environment
used CPython 3.12.13 and NumPy 2.3.5.  Every
finite decision is made with integer arithmetic or Python `Fraction`; no
floating-point trigonometric value is used.

The reference outputs cover 8,916 `(Q,s)` pairs in the `s>1` box, 39,232
eligible critical `(Q,y)` pairs, and all 712 denominators `4 <= Q <= 715`.
The <span style="color: #0000ff">three</span> redundant audits also pass.  The final PDF was rendered page by page
and checked for missing content, undefined references, box warnings, and
metadata.

Optional redundant audits:

```bash
python -I tmp_s1_global_independent_verify.py
python -I tmp_s1_pure_python_audit.py
python -I tmp_s_gt1_pure_python_audit.py
```

## SHA-256

<pre style="color: #0000ff">
76db33224acaae671b1d17f8be1d8dafeb7c493fa3665f7dad66e2a98d29dbfb  sc_s_gt1_near_certificate.py
97c035f3a8fdc556e9acf0db9ca378590b8a445f2417dfb1a4b3a5fc15ad8e04  sc_s1_critical_certificate.py
af94572b631fbea2356809af2696ceb51c656ca82c0d74f3fcae7ce8e16723f3  sc_s1_finite_certificate.py
5f8d9896973b941a5b0971e91d24d1ffde0d32aae4b2d11d1ec52f73baf119b3  tmp_s1_global_independent_verify.py
9db9eae977d5f97e19e9fceeaf70e13970844094c04d255f5ecbd93d6931fe49  tmp_s1_pure_python_audit.py
86304abf20e51c9096de9e552a4a14f178ccfa1890e72d57228aaa3678926edb  tmp_s_gt1_pure_python_audit.py
</pre>

The mathematical route is:

```text
minimum-gcd Fourier layer
  -> subcritical inverse-sine rigidity (SC)
  -> one-third theorem
  -> rate-three balanced-word deletion
  -> rigid binary extension
  -> induction
  -> Fraenkel's conjecture
```
