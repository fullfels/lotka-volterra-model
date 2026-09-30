"""Simulate a deer-wolf system with the Lotka-Volterra equations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import odeint


ALPHA = 1.0397
BETA = 0.0205
DELTA = 0.0001025
GAMMA = 0.1022
INITIAL_DEER = 1521
INITIAL_WOLVES = 65


def derivatives(
    state: tuple[float, float] | np.ndarray,
    _time: float,
    alpha: float = ALPHA,
    beta: float = BETA,
    delta: float = DELTA,
    gamma: float = GAMMA,
) -> tuple[float, float]:
    """Return the Lotka-Volterra derivatives for prey and predators."""
    deer, wolves = state
    return alpha * deer - beta * deer * wolves, delta * deer * wolves - gamma * wolves


def equilibrium(
    alpha: float = ALPHA,
    beta: float = BETA,
    delta: float = DELTA,
    gamma: float = GAMMA,
) -> tuple[float, float]:
    """Return the non-zero equilibrium point (deer, wolves)."""
    return gamma / delta, alpha / beta


def simulate(
    years: float = 100,
    points: int = 2000,
    initial: tuple[float, float] = (INITIAL_DEER, INITIAL_WOLVES),
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Integrate the model over time."""
    time = np.linspace(0, years, points)
    deer, wolves = odeint(derivatives, initial, time).T
    return time, deer, wolves


def conserved_quantity(deer: np.ndarray, wolves: np.ndarray) -> np.ndarray:
    """Evaluate the analytical invariant of the Lotka-Volterra system."""
    return DELTA * deer - GAMMA * np.log(deer) + BETA * wolves - ALPHA * np.log(wolves)


def save_plots(output_dir: Path, time: np.ndarray, deer: np.ndarray, wolves: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(time, deer, label="Deer", linewidth=2)
    ax.plot(time, wolves, label="Wolves", linewidth=2)
    ax.set(title="Deer and wolf population dynamics", xlabel="Time (years)", ylabel="Population")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "population_dynamics.png", dpi=160)
    plt.close(fig)

    deer_eq, wolves_eq = equilibrium()
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(deer, wolves, linewidth=2, label="trajectory")
    ax.scatter(deer_eq, wolves_eq, color="crimson", s=35, label="equilibrium", zorder=3)
    ax.set(title="Lotka-Volterra phase portrait", xlabel="Deer", ylabel="Wolves")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "phase_portrait.png", dpi=160)
    plt.close(fig)

    fig = plt.figure(figsize=(9, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(time, deer, wolves, linewidth=1.8)
    ax.set(title="System trajectory", xlabel="Time (years)", ylabel="Deer", zlabel="Wolves")
    fig.tight_layout()
    fig.savefig(output_dir / "trajectory_3d.png", dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--years", type=float, default=100)
    parser.add_argument("--points", type=int, default=2000)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()

    time, deer, wolves = simulate(args.years, args.points)
    save_plots(args.output_dir, time, deer, wolves)
    invariant = conserved_quantity(deer, wolves)
    deer_eq, wolves_eq = equilibrium()
    summary = {
        "equilibrium_deer": round(float(deer_eq), 2),
        "equilibrium_wolves": round(float(wolves_eq), 2),
        "deer_range": [round(float(deer.min()), 2), round(float(deer.max()), 2)],
        "wolf_range": [round(float(wolves.min()), 2), round(float(wolves.max()), 2)],
        "max_invariant_drift": float(np.max(np.abs(invariant - invariant[0]))),
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
