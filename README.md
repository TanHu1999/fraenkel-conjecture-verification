# Finite-case numerical verification for Fraenkel's conjecture

This repository contains the code used for the finite-case numerical
verification accompanying the manuscript *A  Proof of
Fraenkel's Conjecture*.

Here, “numerical verification” means a finite computational check.  The
decisive programs use exact integer or rational arithmetic and directed
rounding; they do not rely on floating-point trigonometric approximations.
The code is a reproducibility artifact for the manuscript and is not a
standalone substitute for its mathematical arguments.

## Verification programs

The following three files are the finite-case verifiers used by the
manuscript:

- `sc_s_gt1_near_certificate.py`
- `sc_s1_critical_certificate.py`
- `sc_s1_finite_certificate.py`

The following files provide logically redundant independent checks:

- `tmp_s_gt1_pure_python_audit.py`
- `tmp_s1_global_independent_verify.py`
- `tmp_s1_pure_python_audit.py`

Further technical details and reference outputs are recorded in
`fraenkel_proof_README.md`.

## Running the verification

The reference environment used CPython 3.12.13 and NumPy 2.3.5.  From the
repository root, run:

```bash
python -I sc_s_gt1_near_certificate.py
python -I sc_s1_critical_certificate.py
python -I sc_s1_finite_certificate.py
```

Each command must end with `certificate passed`.

Optional independent audits can be run with:

```bash
python -I tmp_s1_global_independent_verify.py
python -I tmp_s1_pure_python_audit.py
python -I tmp_s_gt1_pure_python_audit.py
```

## Lean formalization

A Lean formal verification is in progress and is expected to be uploaded to
this same repository within one month after this version is made public.

