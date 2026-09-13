"""Fiberlock QBER tape — monitor the channel, not the plant.

Live wrap gate uses QBER_MAX=0.11 (DV-QKD / Shor-Preskill abort).
CV-QKD in the field is usually scored as excess noise ξ in shot-noise
units, abort near ξ ≈ 0.05–0.10 SNU, not 11% bit flips.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from platforms.fiberlock.src.application.session import QBER_MAX, WrapRefused

XI_MAX_SNU = 0.08
WINDOW = 16


@dataclass
class Sample:
    observed_at: str
    qber: float
    xi_snu: float | None
    key_bits: int


@dataclass
class Tape:
    span_id: str
    session_id: str
    samples: list[Sample] = field(default_factory=list)
    aborted: bool = False
    abort_reason: str | None = None


def record(tape: Tape, sample: Sample) -> Tape:
    tape.samples.append(sample)
    window = tape.samples[-WINDOW:]
    mean_qber = sum(s.qber for s in window) / len(window)
    xi_vals = [s.xi_snu for s in window if s.xi_snu is not None]
    mean_xi = sum(xi_vals) / len(xi_vals) if xi_vals else None
    if mean_qber >= QBER_MAX:
        tape.aborted = True
        tape.abort_reason = f"rolling QBER {mean_qber:.3f} >= {QBER_MAX}"
        raise WrapRefused(tape.abort_reason)
    if mean_xi is not None and mean_xi >= XI_MAX_SNU:
        tape.aborted = True
        tape.abort_reason = f"rolling excess noise {mean_xi:.3f} SNU >= {XI_MAX_SNU}"
        raise WrapRefused(tape.abort_reason)
    return tape


def can_wrap(tape: Tape) -> bool:
    return (not tape.aborted) and bool(tape.samples)
