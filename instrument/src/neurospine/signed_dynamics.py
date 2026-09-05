"""Signed linear dynamics for inhibitory regulation (ADR-015).

The directed random walk in `circuit.py` is excitatory-only: a
row-stochastic matrix conserves probability, so an edge can only MOVE
activation, never SUPPRESS it. Inhibition is subtraction, which a
stochastic matrix structurally cannot express. Ablation 2 in the ADR-014
threat experiment surfaced this exactly: adding a PFC -> amygdala edge
INCREASED effector drive, the opposite of real top-down downregulation.

The correct object is a linear rate model (a linear dynamical system):

    dx/dt = (W - gamma * I) x + B u

where `W` carries SIGNED weights (excitatory > 0, inhibitory < 0),
`gamma` is a leak term that guarantees stability, `B` maps an exogenous
stimulus `u` onto the regions it drives, and `x` is the regional
activation. For a sustained stimulus the system relaxes to a steady
state

    x_ss = (gamma * I - W)^{-1} B u

which is the equilibrium activation across every region. Effectors are
LINEAR READOUTS of that steady state (an effector's drive is a weighted
sum of the neural activation it receives), so no probability-conservation
constraint is imposed on them.

External anchors (both permit and use signed / negative weights):

- Gu et al. 2015, "Controllability of structural brain networks"
  (Nat. Commun.): the discrete linear system x_{t+1} = A x_t + B u_t on a
  brain graph, with the controllability Gramian and minimum control
  energy. This module uses the continuous-time leaky analogue and the
  same Gramian / control-energy machinery.
- Galan 2008, "On how network architecture determines the dominant
  patterns of spontaneous neural activity" (PLoS ONE): a linear
  stochastic rate model of resting-state dynamics on the connectome.

Nothing here re-derives probability math from `dynamics.py`; this is a
distinct (linear-algebraic, signed) regime that lives beside it.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import solve_continuous_lyapunov


@dataclass
class SignedLinearSystem:
    """A continuous-time leaky linear rate model on a signed graph.

    - `W`: signed weighted connectivity, `W[i, j]` is the effect of region
      `j` on region `i` (excitatory > 0, inhibitory < 0). Diagonal is
      treated as zero; self-decay is supplied by `gamma`.
    - `gamma`: scalar leak. The dynamics matrix is `A = W - gamma * I`.
      Stability (all eigenvalues of `A` in the left half plane) requires
      `gamma > max(Re(eig(W)))`; `build_signed_system` picks it that way.
    - `labels`: node labels, index-aligned with `W`.
    """

    W: np.ndarray
    gamma: float
    labels: list

    def __post_init__(self) -> None:
        self.W = np.asarray(self.W, dtype=float)
        if self.W.ndim != 2 or self.W.shape[0] != self.W.shape[1]:
            raise ValueError("W must be square")
        if len(self.labels) != self.W.shape[0]:
            raise ValueError("labels must be index-aligned with W")

    @property
    def n(self) -> int:
        return self.W.shape[0]

    @property
    def A(self) -> np.ndarray:
        """Dynamics matrix `A = W - gamma I` (zero diagonal on W)."""
        Wz = self.W.copy()
        np.fill_diagonal(Wz, 0.0)
        return Wz - self.gamma * np.eye(self.n)

    def index_of(self, label_substr: str) -> list:
        s = label_substr.lower()
        return [i for i, l in enumerate(self.labels) if s in str(l).lower()]

    def is_stable(self) -> bool:
        """True iff every eigenvalue of A has strictly negative real part
        (the steady state exists and is globally attracting)."""
        return float(np.max(np.real(np.linalg.eigvals(self.A)))) < 0.0

    def spectral_abscissa(self) -> float:
        """max Re(eig(A)); < 0 means stable, and its magnitude is the
        slowest relaxation rate."""
        return float(np.max(np.real(np.linalg.eigvals(self.A))))

    def steady_state(self, u: np.ndarray) -> np.ndarray:
        """Equilibrium activation `x_ss = -A^{-1} u` under constant input
        `u` (already mapped onto regions). Requires a stable system."""
        u = np.asarray(u, dtype=float)
        if not self.is_stable():
            raise ValueError(
                "system is unstable; steady state is not defined "
                f"(spectral abscissa {self.spectral_abscissa():.3f} >= 0)"
            )
        return np.linalg.solve(-self.A, u)

    def simulate(
        self, x0: np.ndarray, u: np.ndarray, steps: int, dt: float = 0.01
    ) -> np.ndarray:
        """Forward-Euler trajectory of `dx/dt = A x + u`. Returns an array
        of shape (steps + 1, n). For validation and for showing the
        transient, not just the equilibrium."""
        x = np.asarray(x0, dtype=float).copy()
        u = np.asarray(u, dtype=float)
        A = self.A
        traj = [x.copy()]
        for _ in range(steps):
            x = x + dt * (A @ x + u)
            traj.append(x.copy())
        return np.array(traj)

    def controllability_gramian(self, control_nodes: list) -> np.ndarray:
        """Infinite-horizon controllability Gramian for driving the system
        from the `control_nodes` (input channels). Solves the Lyapunov
        equation `A Wc + Wc A^T + B B^T = 0`. Larger Gramian eigenvalues
        mean cheaper control. Requires a stable A."""
        if not self.is_stable():
            raise ValueError("controllability Gramian requires a stable A")
        B = np.zeros((self.n, len(control_nodes)))
        for k, idx in enumerate(control_nodes):
            B[idx, k] = 1.0
        # solve_continuous_lyapunov solves A X + X A^T = Q for X; we need
        # A Wc + Wc A^T = -B B^T, so Q = -B B^T.
        return solve_continuous_lyapunov(self.A, -B @ B.T)

    def minimum_control_energy(
        self, control_nodes: list, target_state: np.ndarray
    ) -> float:
        """Minimum control energy to steer the system to `target_state`
        using only `control_nodes`, in the infinite-horizon limit:
        `E = x_T^T Wc^{-1} x_T` where `Wc` is the controllability Gramian.
        Lower is easier to reach. This quantifies how hard it is for a
        control set (e.g. prefrontal cortex) to impose a target activation
        (e.g. a downregulated amygdala)."""
        Wc = self.controllability_gramian(control_nodes)
        xT = np.asarray(target_state, dtype=float)
        return float(xT @ np.linalg.solve(Wc, xT))


def build_signed_system(
    fc: np.ndarray,
    node_labels: list,
    networks: np.ndarray,
    excitatory_edges: list,
    inhibitory_edges: list,
    exc_weight: float = 1.0,
    inh_weight: float = 1.0,
    fc_scale: float = 0.5,
    fc_threshold: float = 0.0,
    leak_margin: float = 1.0,
    gamma: float | None = None,
) -> SignedLinearSystem:
    """Assemble a signed linear system from measured FC plus signed
    directed anatomical priors.

    - `fc`: symmetric measured connectivity (correlational, non-negative
      part is used as a weak symmetric excitatory backbone, scaled by
      `fc_scale`).
    - `excitatory_edges` / `inhibitory_edges`: lists of `DirectedEdge`
      (from `circuit.py`), matched to regions by label substring.
      Excitatory add `+exc_weight * edge.weight`, inhibitory add
      `-inh_weight * edge.weight` to `W[target, source]`.
    - `leak_margin`: when `gamma` is not given, `gamma = max(Re(eig(W)))
      + leak_margin`, so the system is guaranteed stable with a bounded
      steady state.
    - `gamma`: optional explicit leak. Pass it to hold the leak fixed
      across a parameter sweep (e.g. varying inhibitory gain) so the only
      thing changing is the edge under study, not the global relaxation
      rate. A `ValueError` is raised if the given `gamma` does not
      stabilize the system.

    Note the convention: `W[i, j]` is the effect of `j` on `i`, so a
    directed prior `source -> target` writes `W[target, source]`.
    """
    n = fc.shape[0]
    labels = list(node_labels)

    # Symmetric excitatory backbone from the non-negative part of FC.
    W = np.where(fc >= fc_threshold, np.maximum(fc, 0.0), 0.0).astype(float)
    np.fill_diagonal(W, 0.0)
    W *= fc_scale

    def match(substr):
        s = substr.lower()
        return [i for i in range(n) if s in str(labels[i]).lower()]

    for edge in excitatory_edges:
        for si in match(edge.source):
            for ti in match(edge.target):
                W[ti, si] += exc_weight * edge.weight  # effect of si on ti
    for edge in inhibitory_edges:
        for si in match(edge.source):
            for ti in match(edge.target):
                W[ti, si] -= inh_weight * edge.weight

    if gamma is None:
        gamma = float(np.max(np.real(np.linalg.eigvals(W)))) + leak_margin
    sys = SignedLinearSystem(W=W, gamma=gamma, labels=labels)
    if not sys.is_stable():
        raise ValueError(
            f"given gamma={gamma:.3f} does not stabilize the system "
            f"(spectral abscissa {sys.spectral_abscissa():.3f} >= 0)"
        )
    return sys
