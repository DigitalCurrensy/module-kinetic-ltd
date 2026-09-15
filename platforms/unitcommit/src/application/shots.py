"""Unitcommit shot backend — exact statevector, n <= 4.

H^\otimes n then p layers of RZ/RZZ (H_C) and RX (H_M). Expectation is
Σ |a_z|^2 cost(z). Majority bitstring is the mode over shots.
No Qiskit. qaoa.py / spsa.py / build_ising.py stay frozen.
Module Kinetic Ltd.
"""
from __future__ import annotations

import cmath
import math

from platforms.unitcommit.src.application.build_ising import IsingProblem
from platforms.unitcommit.src.application.qaoa import QaoaCircuit, WidthMismatch, cost

MAX_N = 4


class ShotError(Exception):
    code = "shot_error"


class TooWide(ShotError):
    code = "too_wide"


def _bits(index: int, n: int) -> tuple[int, ...]:
    return tuple((index >> q) & 1 for q in range(n))


def _apply_h_all(amps: list[complex], n: int) -> None:
    dim = 1 << n
    scale = 1.0 / math.sqrt(2.0)
    for q in range(n):
        nxt = amps[:]
        bit = 1 << q
        for z in range(dim):
            if z & bit:
                continue
            a0, a1 = amps[z], amps[z | bit]
            nxt[z] = scale * (a0 + a1)
            nxt[z | bit] = scale * (a0 - a1)
        amps[:] = nxt


def _apply_rz(amps: list[complex], n: int, q: int, angle: float) -> None:
    dim = 1 << n
    bit = 1 << q
    phase0 = cmath.exp(-1j * angle / 2.0)
    phase1 = cmath.exp(1j * angle / 2.0)
    for z in range(dim):
        amps[z] *= phase1 if (z & bit) else phase0


def _apply_rzz(amps: list[complex], n: int, i: int, j: int, angle: float) -> None:
    dim = 1 << n
    bi, bj = 1 << i, 1 << j
    plus = cmath.exp(-1j * angle / 2.0)
    minus = cmath.exp(1j * angle / 2.0)
    for z in range(dim):
        same = ((z & bi) != 0) == ((z & bj) != 0)
        amps[z] *= plus if same else minus


def _apply_rx(amps: list[complex], n: int, q: int, angle: float) -> None:
    dim = 1 << n
    bit = 1 << q
    c = math.cos(angle / 2.0)
    s = -1j * math.sin(angle / 2.0)
    nxt = amps[:]
    for z in range(dim):
        if z & bit:
            continue
        a0, a1 = amps[z], amps[z | bit]
        nxt[z] = c * a0 + s * a1
        nxt[z | bit] = s * a0 + c * a1
    amps[:] = nxt


def statevector(problem: IsingProblem, circuit: QaoaCircuit) -> tuple[complex, ...]:
    n = circuit.n
    if n != problem.n:
        raise WidthMismatch(f"circuit n={n} != problem n={problem.n}")
    if n > MAX_N:
        raise TooWide(f"shot backend refuses n={n} > {MAX_N}")
    amps = [0j] * (1 << n)
    amps[0] = 1.0 + 0j
    _apply_h_all(amps, n)
    for layer in circuit.layers:
        for q, h_i in enumerate(problem.h):
            _apply_rz(amps, n, q, 2.0 * layer.gamma * h_i)
        for i, j, w in problem.j_coo:
            _apply_rzz(amps, n, i, j, 2.0 * layer.gamma * w)
        for q in range(n):
            _apply_rx(amps, n, q, 2.0 * layer.beta)
    return tuple(amps)


def expectation(problem: IsingProblem, circuit: QaoaCircuit) -> float:
    amps = statevector(problem, circuit)
    total = 0.0
    for z, a in enumerate(amps):
        total += (a.real * a.real + a.imag * a.imag) * cost(problem, _bits(z, circuit.n))
    return total


def _lcg(seed: int) -> int:
    return (1103515245 * seed + 12345) & 0x7FFFFFFF


def sample_majority(
    problem: IsingProblem,
    circuit: QaoaCircuit,
    *,
    shots: int,
    seed: int,
) -> tuple[int, ...]:
    if shots < 1:
        raise ShotError("need at least one shot")
    amps = statevector(problem, circuit)
    cdf: list[float] = []
    acc = 0.0
    for a in amps:
        acc += a.real * a.real + a.imag * a.imag
        cdf.append(acc)
    counts = [0] * len(amps)
    x = seed & 0x7FFFFFFF or 1
    for _ in range(shots):
        x = _lcg(x)
        u = x / 2147483647.0 * cdf[-1]
        picked = 0
        for z, edge in enumerate(cdf):
            if u <= edge:
                picked = z
                break
        counts[picked] += 1
    winner = max(range(len(counts)), key=lambda z: counts[z])
    return _bits(winner, circuit.n)
