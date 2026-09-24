"""A description of the on and off plan.

This file does not call a quantum computer. The plan width must match.
"""
from __future__ import annotations

from dataclasses import dataclass

from platforms.unitcommit.src.application.build_ising import IsingProblem


class QaoaError(Exception):
    code = "qaoa_error"


class DepthRefused(QaoaError):
    code = "depth_refused"


class WidthMismatch(QaoaError):
    code = "width_mismatch"


MAX_P = 3


@dataclass(frozen=True)
class QaoaLayer:
    gamma: float
    beta: float


@dataclass(frozen=True)
class QaoaCircuit:
    n: int
    p: int
    layers: tuple[QaoaLayer, ...]
    mixer: str = "x"


def from_ising(problem: IsingProblem, *,
    p: int = 1,
    gammas: tuple[float, ...] | None = None,
    betas: tuple[float, ...] | None = None,
) -> QaoaCircuit:
    if p < 1 or p > MAX_P:
        raise DepthRefused(f"QAOA depth p={p} outside 1..{MAX_P}")
    gammas = gammas or tuple(0.5 / p for _ in range(p))
    betas = betas or tuple(0.4 / p for _ in range(p))
    if len(gammas) != p or len(betas) != p:
        raise DepthRefused("gamma/beta length must equal p")
    layers = tuple(QaoaLayer(g, b) for g, b in zip(gammas, betas))
    return QaoaCircuit(n=problem.n, p=p, layers=layers)


def cost(problem: IsingProblem, bits: tuple[int, ...]) -> float:
    if len(bits) != problem.n:
        raise WidthMismatch(f"bitstring width {len(bits)} != n={problem.n}")
    sigma = tuple(2 * b - 1 for b in bits)
    e = 0.0
    for i, hi in enumerate(problem.h):
        e += hi * sigma[i]
    for i, j, w in problem.j_coo:
        e += w * sigma[i] * sigma[j]
    return e


def decode_assignment(problem: IsingProblem) -> tuple[int, ...]:
    """p→0 field decode: u=1 if -h_i > 0. Width is always n."""
    return tuple(1 if -hi > 0 else 0 for hi in problem.h)
