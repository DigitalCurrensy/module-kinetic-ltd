"""A small exact sample of the on and off plan. Not an account on a quantum computer."""
from __future__ import annotations

from cmath import exp
from math import cos, sin

from platforms.unitcommit.src.application.build_ising import IsingProblem
from platforms.unitcommit.src.application.qaoa import QaoaCircuit, WidthMismatch

MAX_N = 4


class ShotError(Exception):
    code = "shot_error"


class WidthRefused(ShotError):
    code = "width_refused"


def _plus(n: int) -> list[complex]:
    amp = 2 ** (-0.5 * n)
    return [amp] * (1 << n)


def _apply_rz(state: list[complex], qubit: int, angle: float) -> None:
    n = len(state)
    half = 1 << qubit
    for i in range(n):
        sign = 1.0 if (i & half) == 0 else -1.0
        state[i] *= exp(-0.5j * angle * sign)


def _apply_rzz(state: list[complex], q_i: int, q_j: int, angle: float) -> None:
    n = len(state)
    mi, mj = 1 << q_i, 1 << q_j
    for idx in range(n):
        zi = 1.0 if (idx & mi) == 0 else -1.0
        zj = 1.0 if (idx & mj) == 0 else -1.0
        state[idx] *= exp(-0.5j * angle * zi * zj)


def _apply_rx(state: list[complex], qubit: int, angle: float) -> None:
    n = len(state)
    half = 1 << qubit
    c, s = cos(angle / 2.0), -1j * sin(angle / 2.0)
    seen = [False] * n
    for i in range(n):
        j = i ^ half
        if seen[i] or seen[j]:
            continue
        a, b = state[i], state[j]
        state[i] = c * a + s * b
        state[j] = s * a + c * b
        seen[i] = seen[j] = True


def prepare(problem: IsingProblem, circuit: QaoaCircuit) -> list[complex]:
    if problem.n != circuit.n:
        raise WidthMismatch(f"circuit n={circuit.n} != problem n={problem.n}")
    if problem.n > MAX_N:
        raise WidthRefused(f"exact backend refuses n={problem.n} > {MAX_N}")
    state = _plus(problem.n)
    for layer in circuit.layers:
        for i, hi in enumerate(problem.h):
            _apply_rz(state, i, 2.0 * layer.gamma * hi)
        for i, j, w in problem.j_coo:
            _apply_rzz(state, i, j, 2.0 * layer.gamma * w)
        for i in range(problem.n):
            _apply_rx(state, i, 2.0 * layer.beta)
    return state


def probabilities(state: list[complex]) -> tuple[float, ...]:
    return tuple(abs(a) ** 2 for a in state)


def majority(state: list[complex], n: int) -> tuple[int, ...]:
    probs = probabilities(state)
    winner = max(range(len(probs)), key=lambda k: probs[k])
    return tuple((winner >> q) & 1 for q in range(n))


def expectation(problem: IsingProblem, state: list[complex]) -> float:
    probs = probabilities(state)
    energy = 0.0
    for bits, p in enumerate(probs):
        sigma = tuple(1.0 if (bits >> q) & 1 else -1.0 for q in range(problem.n))
        e = 0.0
        for i, hi in enumerate(problem.h):
            e += hi * sigma[i]
        for i, j, w in problem.j_coo:
            e += w * sigma[i] * sigma[j]
        energy += p * e
    return energy
