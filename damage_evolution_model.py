# ============================================================
# damage_evolution_model.py
# Physics-based stochastic damage evolution model (validated form)
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


PRONOSTIA_FITTED = {
    "k": 9.94e-7,
    "a": 0.96,
    "b": 0.0,
    "c": 1.03,
    "d": 0.0,
    "beta": 2.01,
    "sigma": 0.498,
}


@dataclass
class OperatingCondition:
    Load: float
    Speed: float
    Temperature: float = 1.0
    Lubrication: float = 1.0


def damage_evolution_deterministic(
    machine: OperatingCondition | dict,
    t: np.ndarray,
    dt: float = 1.0,
    k: float = PRONOSTIA_FITTED["k"],
    a: float = PRONOSTIA_FITTED["a"],
    b: float = PRONOSTIA_FITTED["b"],
    c: float = PRONOSTIA_FITTED["c"],
    d: float = PRONOSTIA_FITTED["d"],
    beta: float = PRONOSTIA_FITTED["beta"],
    D0: float = 1e-4,
) -> np.ndarray:

    if isinstance(machine, dict):
        machine = OperatingCondition(
            Load=machine["Load"],
            Speed=machine["Speed"],
            Temperature=machine.get("Temperature", 1.0),
            Lubrication=machine.get("Lubrication", 1.0),
        )

    base_rate = (
        k
        * (machine.Load ** a)
        * (machine.Speed ** c)
        * (machine.Temperature ** b)
        * (machine.Lubrication ** (-d))
    )

    n = len(t)
    D = np.zeros(n)
    D[0] = D0

    for i in range(1, n):
        growth = base_rate * (D[i - 1] ** beta)
        D[i] = D[i - 1] + growth * dt

        if D[i] >= 1.0:
            D[i:] = 1.0
            break
        if D[i] < D0:
            D[i] = D0

    return D


def damage_evolution_stochastic(
    machine: OperatingCondition | dict,
    t: np.ndarray,
    dt: float = 1.0,
    k: float = PRONOSTIA_FITTED["k"],
    a: float = PRONOSTIA_FITTED["a"],
    b: float = PRONOSTIA_FITTED["b"],
    c: float = PRONOSTIA_FITTED["c"],
    d: float = PRONOSTIA_FITTED["d"],
    beta: float = PRONOSTIA_FITTED["beta"],
    sigma: float = PRONOSTIA_FITTED["sigma"],
    D0: float = 1e-4,
    rng: Optional[np.random.Generator] = None,
) -> tuple[np.ndarray, Optional[int]]:

    if rng is None:
        rng = np.random.default_rng()

    if isinstance(machine, dict):
        machine = OperatingCondition(
            Load=machine["Load"],
            Speed=machine["Speed"],
            Temperature=machine.get("Temperature", 1.0),
            Lubrication=machine.get("Lubrication", 1.0),
        )

    K_i = float(np.exp(np.log(k) + sigma * rng.standard_normal()))

    base_rate = (
        K_i
        * (machine.Load ** a)
        * (machine.Speed ** c)
        * (machine.Temperature ** b)
        * (machine.Lubrication ** (-d))
    )

    n = len(t)
    D = np.zeros(n)
    D[0] = D0
    failure_step: Optional[int] = None

    for i in range(1, n):
        growth = base_rate * (D[i - 1] ** beta)
        D[i] = D[i - 1] + growth * dt

        if D[i] >= 1.0:
            D[i:] = 1.0
            failure_step = i
            break
        if D[i] < D0:
            D[i] = D0

    return D, failure_step


def damage_evolution_model(
    machine: OperatingCondition | dict,
    t: np.ndarray,
    dt: float = 1.0,
    k: float = PRONOSTIA_FITTED["k"],
    a: float = PRONOSTIA_FITTED["a"],
    b: float = PRONOSTIA_FITTED["b"],
    c: float = PRONOSTIA_FITTED["c"],
    d: float = PRONOSTIA_FITTED["d"],
    beta: float = PRONOSTIA_FITTED["beta"],
    sigma: float = PRONOSTIA_FITTED["sigma"],
    D0: float = 1e-4,
    rng: Optional[np.random.Generator] = None,
    deterministic: bool = False,
) -> np.ndarray:

    if deterministic:
        return damage_evolution_deterministic(
            machine, t, dt, k, a, b, c, d, beta, D0
        )
    D, _ = damage_evolution_stochastic(
        machine, t, dt, k, a, b, c, d, beta, sigma, D0, rng
    )
    return D


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    machine = OperatingCondition(Load=4000, Speed=1800)
    t = np.arange(5000)
    rng = np.random.default_rng(seed=42)

    fig, ax = plt.subplots(figsize=(10, 6))

    for _ in range(30):
        D, failure = damage_evolution_stochastic(machine, t, rng=rng)
        ax.plot(D, alpha=0.3, color="steelblue", linewidth=0.8)

    D_det = damage_evolution_deterministic(machine, t)
    ax.plot(D_det, color="crimson", linewidth=2, label="Deterministic (mean)")

    ax.axhline(1.0, color="black", linestyle=":", linewidth=1, label="Failure (D=1)")
    ax.set_xlabel("Cycle")
    ax.set_ylabel("Damage D")
    ax.set_title("Stochastic damage evolution (30 realisations) at "
                 "1800 rpm, 4000 N (PRONOSTIA Condition 1)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("damage_evolution_demo.png", dpi=150)
    print("Demonstration chart saved to damage_evolution_demo.png")
