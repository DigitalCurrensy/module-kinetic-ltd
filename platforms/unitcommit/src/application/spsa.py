"""A small adjustment of the plan settings.

At the center it stays put. Away from the center it moves. Not a quantum computer account.
"""
from __future__ import annotations

from dataclasses import dataclass

from platforms.unitcommit.src.application.build_ising import IsingProblem
from platforms.unitcommit.src.application.qaoa import (
    DepthRefused,
    MAX_P,
    QaoaCircuit,
    cost,
    decode_assignment,
    from_ising,
)


class SpsaError(Exception):
    code = "spsa_error"


@dataclass(frozen=True)
class SpsaStep:
    gammas: tuple[float, ...]
    betas: tuple[float, ...]
    loss: float


def _bernoulli(seed: int, n: int) -> tuple[int, ...]:
    out = []
    x = seed & 0xFFFFFFFF
    for _ in range(n):
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        out.append(1 if (x & 1) else -1)
    return tuple(out)


def surrogate_loss(
    problem: IsingProblem,
    gammas: tuple[float, ...],
    betas: tuple[float, ...],
) -> float:
    bits = decode_assignment(problem)
    pull = sum((g - 0.5) ** 2 + (b - 0.4) ** 2 for g, b in zip(gammas, betas))
    return cost(problem, bits) + pull


def step(
    problem: IsingProblem,
    gammas: tuple[float, ...],
    betas: tuple[float, ...],
    *,
    a: float,
    c: float,
    seed: int,
) -> SpsaStep:
    p = len(gammas)
    if p != len(betas) or p < 1 or p > MAX_P:
        raise DepthRefused(f"SPSA depth p={p} outside 1..{MAX_P}")
    dg = _bernoulli(seed, p)
    db = _bernoulli(seed + 1, p)
    g_plus = tuple(g + c * d for g, d in zip(gammas, dg))
    g_minus = tuple(g - c * d for g, d in zip(gammas, dg))
    b_plus = tuple(b + c * d for b, d in zip(betas, db))
    b_minus = tuple(b - c * d for b, d in zip(betas, db))
    y_plus = surrogate_loss(problem, g_plus, b_plus)
    y_minus = surrogate_loss(problem, g_minus, b_minus)
    slope = (y_plus - y_minus) / (2.0 * c)
    gammas_n = tuple(g - a * slope / d for g, d in zip(gammas, dg))
    betas_n = tuple(b - a * slope / d for b, d in zip(betas, db))
    loss = surrogate_loss(problem, gammas_n, betas_n)
    return SpsaStep(gammas_n, betas_n, loss)


def optimize(
    problem: IsingProblem,
    *,
    p: int = 1,
    steps: int = 4,
    a0: float = 0.05,
    c0: float = 0.05,
    seed: int = 7,
) -> QaoaCircuit:
    if steps < 1:
        raise SpsaError("need at least one SPSA step")
    circuit = from_ising(problem, p=p)
    gammas = tuple(layer.gamma for layer in circuit.layers)
    betas = tuple(layer.beta for layer in circuit.layers)
    for k in range(steps):
        landed = step(
            problem,
            gammas,
            betas,
            a=a0 / (k + 1),
            c=c0 / ((k + 1) ** 0.5),
            seed=seed + k,
        )
        gammas, betas = landed.gammas, landed.betas
    return from_ising(problem, p=p, gammas=gammas, betas=betas)
