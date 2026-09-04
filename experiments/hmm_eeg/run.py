"""ADR-012: does a hidden Markov model beat a first-order model on the
EEG covariance trajectory, beyond a first-order-null control?

Council review (ADR-011) showed that discretizing a continuous SPD
process manufactures apparent non-Markovianity, so a plain Markov test
on prototype labels is confounded. This experiment avoids discretization
entirely: it embeds each SPD covariance into the AIRM tangent space at
the group Frechet mean (a norm-preserving Euclidean coordinate) and asks
a sharper question.

VAR(1), a first-order vector autoregression, is the canonical first-order
Markov model for continuous data: x_{t+1} = c + A x_t + noise. If a
K-state Gaussian HMM achieves higher held-out log-likelihood than VAR(1)
on the EEG, the EEG carries structure a first-order model misses.

The confound control (shipped WITH the test this time, per ADR-011): fit
VAR(1) to the full EEG series, generate surrogate series from it (which
are first-order Markov by construction), and run the identical
HMM-vs-VAR(1) comparison on each surrogate. On surrogates the HMM should
NOT beat VAR(1) (VAR(1) is the true generator). A subject shows genuine
higher-order structure only when its EEG HMM-minus-VAR(1) held-out gain
exceeds the 95th percentile of the surrogate null.

Run:

    python experiments/hmm_eeg/run.py --subjects 1 2 3 4 5 \
        --n-surrogates 12 --hmm-states 3
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "instrument" / "src"))
sys.path.insert(0, str(REPO_ROOT / "experiments" / "spd_transition_eegbci"))

from neurospine.hmm import GaussianHMM  # noqa: E402
from neurospine.manifold import spd_tangent_embedding  # noqa: E402
from run import epoch_covariances, load_epochs  # noqa: E402


def fit_var1(X: np.ndarray, ridge: float = 1e-3):
    """Least-squares VAR(1): x_{t+1} = A x_t + c + noise. Returns
    (A, c, Sigma) with Sigma the residual covariance."""
    Xt, Xn = X[:-1], X[1:]
    D = X.shape[1]
    Z = np.hstack([Xt, np.ones((len(Xt), 1))])  # design with intercept
    # Ridge-regularized normal equations.
    W = np.linalg.solve(
        Z.T @ Z + ridge * np.eye(D + 1), Z.T @ Xn
    )  # (D+1, D)
    A = W[:D].T          # (D, D)
    c = W[D]             # (D,)
    resid = Xn - (Xt @ A.T + c)
    Sigma = np.cov(resid.T) + ridge * np.eye(D)
    return A, c, Sigma


def var1_heldout_loglik(A, c, Sigma, X_train_last, X_test) -> float:
    """Per-step predictive log-likelihood of VAR(1) on the test block,
    conditioning the first test step on the last training step."""
    D = Sigma.shape[0]
    sign, logdet = np.linalg.slogdet(Sigma)
    Sinv = np.linalg.inv(Sigma)
    prev = X_train_last
    total = 0.0
    for t in range(len(X_test)):
        mu = A @ prev + c
        diff = X_test[t] - mu
        total += -0.5 * (D * np.log(2 * np.pi) + logdet + diff @ Sinv @ diff)
        prev = X_test[t]
    return float(total / len(X_test))


def var1_sample(A, c, Sigma, n, x0, rng) -> np.ndarray:
    D = Sigma.shape[0]
    L = np.linalg.cholesky(Sigma)
    X = np.empty((n, D))
    prev = x0
    for t in range(n):
        X[t] = A @ prev + c + L @ rng.standard_normal(D)
        prev = X[t]
    return X


def hmm_heldout_loglik(X_train, X_test, k, restarts, seed) -> float:
    """Per-step held-out log-likelihood of a K-state Gaussian HMM."""
    hmm = GaussianHMM(
        n_states=k, n_restarts=restarts, random_state=seed, n_iter=60
    ).fit(X_train)
    return hmm.score(X_test) / len(X_test)


def comparison(X, k, restarts, seed, test_frac=0.3):
    """HMM-minus-VAR(1) per-step held-out log-likelihood on a series X."""
    n = len(X)
    split = int(n * (1 - test_frac))
    Xtr, Xte = X[:split], X[split:]
    A, c, Sigma = fit_var1(Xtr)
    var_ll = var1_heldout_loglik(A, c, Sigma, Xtr[-1], Xte)
    hmm_ll = hmm_heldout_loglik(Xtr, Xte, k, restarts, seed)
    return hmm_ll - var_ll, hmm_ll, var_ll


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subjects", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    ap.add_argument("--n-surrogates", type=int, default=12)
    ap.add_argument("--hmm-states", type=int, default=3)
    ap.add_argument("--restarts", type=int, default=3)
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).parent / "results" / "hmm_vs_var1.json")
    args = ap.parse_args()

    rows = []
    print(f"{'subj':>5} {'eeg_gain':>10} {'null_mean':>10} {'null_p95':>10} "
          f"{'p':>7} {'verdict':>14}")
    for subj in args.subjects:
        covs = epoch_covariances(load_epochs(subj))
        X, _ref = spd_tangent_embedding(list(covs))

        eeg_gain, hmm_ll, var_ll = comparison(
            X, args.hmm_states, args.restarts, seed=0
        )

        # Confound control: VAR(1) surrogates of the full series.
        A, c, Sigma = fit_var1(X)
        rng = np.random.default_rng(subj)
        null = []
        for si in range(args.n_surrogates):
            surr = var1_sample(A, c, Sigma, len(X), X[0], rng)
            g, _, _ = comparison(surr, args.hmm_states, args.restarts, seed=si + 1)
            null.append(g)
        null = np.array(null)
        p95 = float(np.percentile(null, 95))
        p = float((null >= eeg_gain).mean())
        genuine = eeg_gain > p95
        verdict = "HMM>VAR1 real" if genuine else "within VAR1 null"
        rows.append({
            "subject": int(subj),
            "eeg_hmm_minus_var1": float(eeg_gain),
            "eeg_hmm_ll": float(hmm_ll),
            "eeg_var1_ll": float(var_ll),
            "surrogate_null_mean": float(null.mean()),
            "surrogate_null_p95": p95,
            "p_vs_null": p,
            "genuine_higher_order": bool(genuine),
        })
        print(f"{subj:>5} {eeg_gain:>10.4f} {null.mean():>10.4f} {p95:>10.4f} "
              f"{p:>7.2f} {verdict:>14}")

    n_real = sum(r["genuine_higher_order"] for r in rows)
    print()
    print(f"{n_real}/{len(rows)} subjects: HMM beats VAR(1) beyond the "
          f"first-order surrogate null.")
    print()
    print("A positive result means the EEG covariance trajectory carries")
    print("latent-state structure that a first-order model (VAR1) misses,")
    print("AND that this exceeds what the pipeline finds on data that IS")
    print("first-order by construction. That is the confound-controlled")
    print("version of the ADR-009 claim.")

    result = {
        "hmm_states": args.hmm_states,
        "n_surrogates": args.n_surrogates,
        "per_subject": rows,
        "n_genuine": int(n_real),
        "n_subjects": len(rows),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
