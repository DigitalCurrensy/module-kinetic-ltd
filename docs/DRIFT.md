# Drift detection — Module Kinetic Ltd

Four independent detectors. Do not collapse them into one score.

## 1. Repo SHA drift (desk hygiene)

Parent `platforms/{house}/path` blob SHA vs child `path` blob SHA.
Match = child is a 1:1 copy of that file. Mismatch = child is stale or import-rewritten.
Bayline receipt.py `49eea447` matches parent. Loadclear refuse.py `04a48547` matches parent.

## 2. Unitcommit clearance drift (commit law)

Live `can_clear` / `require_cleared`:

    residual_mw <= tolerance_mw
    AND assignment_count == problem.n
    AND opf.spin_count == problem.n

Two refuse reasons:
- residual drift: ADMM/AC-OPF did not close the MW books
- assignment drift: annealer dropped or duplicated a spin

Cabinetfield `f` is not this detector. `f` shrinks Pmax before `build_ising`.

## 3. Measurement drift that feeds H

- Cabinetfield: critical illegal unless `calibration_run` covers `observed_at`
- Phasepin: CSAC first; PTP if |offset| < 1_000_000 ns; holdover if < 4 h; else gps_peer
- Fiberlock tape: rolling mean QBER >= 0.11 or ξ >= 0.08 SNU aborts wrap

## 4. Doc vs code (ISING-HAMILTONIAN.md is stale on conversion signs)

Live builder: σ = 2u − 1, x = (σ+1)/2, h += q/2, J = Q/4.
Doc still writes x = (1−σ)/2 and negative h increments. Code is law.
Live defaults λ_L=50 λ_M=40 not the 5000/4000 in the doc example.
