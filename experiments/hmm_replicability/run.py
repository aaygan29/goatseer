"""A1 replicability: do a subject's HMM dynamics replicate across sessions,
BEYOND their marginal covariance?

The naive fingerprinting claim ("I can identify a subject cross-session")
is nearly vacuous: anatomy, skull, and electrode placement make each
subject's MARGINAL covariance distinctive, so any method identifies
subjects at above-chance rates without saying anything about dynamics.
The user's own prior work includes a retracted fingerprinting overclaim
of exactly this kind, so the specificity ablation ships with the test.

The real A1 claim is: a subject's LATENT-STATE DYNAMICS (the HMM
transition structure and state geometry) replicate across sessions, and
identify the subject BETTER than their marginal covariance alone.

Design:

- Two genuinely separate sessions per subject: PhysioNet eegbci
  imagined-fist runs 4 (session A) and 8 (session B).
- Per-epoch SPD covariance, embedded into the AIRM tangent space at a
  SINGLE global reference (Frechet mean of all session-A covariances
  pooled across subjects), so scores are comparable across subjects.
- For each subject i, fit on session A:
    (a) a K-state Gaussian HMM (dynamics + geometry), and
    (b) a static single Gaussian (marginal geometry only, no dynamics)
        = the specificity-ablation baseline.
- Score every subject j's session B under every subject i's model:
  per-step held-out log-likelihood. Two N x N matrices.
- Identification accuracy = fraction of subjects j whose own model
  (i = j) gives the highest score on their session B. Chance = 1/N.
- The claim holds only if HMM identification EXCEEDS static
  identification: dynamics must add identifying information beyond the
  marginal. If HMM == static, the "dynamics replicate" claim is empty.

Run:

    python experiments/hmm_replicability/run.py --subjects 1 2 3 4 5 6 7 8 \
        --hmm-states 3
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
from neurospine.manifold import (  # noqa: E402
    airm_frechet_mean,
    spd_tangent_vector,
)
from run import epoch_covariances  # noqa: E402

SENSORIMOTOR = ["C3", "C4", "Cz", "Fz", "Pz"]


def load_run_covs(subject: int, run: int, epoch_seconds: float = 2.0) -> np.ndarray:
    """SPD covariances for one subject, one run."""
    import mne
    from mne.datasets import eegbci

    files = eegbci.load_data(subject, runs=[run], update_path=True, verbose="ERROR")
    raws = [mne.io.read_raw_edf(f, preload=True, verbose="ERROR") for f in files]
    raw = mne.concatenate_raws(raws)
    eegbci.standardize(raw)
    raw.set_montage("standard_1020", on_missing="ignore")
    raw.pick(SENSORIMOTOR, verbose="ERROR")
    raw.set_eeg_reference("average", projection=False, verbose="ERROR")
    raw.filter(8.0, 30.0, fir_design="firwin", verbose="ERROR")
    sfreq = raw.info["sfreq"]
    w = int(round(epoch_seconds * sfreq))
    data = raw.get_data()
    nch, ntot = data.shape
    ne = ntot // w
    epochs = data[:, : ne * w].reshape(nch, ne, w).transpose(1, 0, 2)
    return epoch_covariances(epochs)


def static_gaussian_loglik(X: np.ndarray, mean: np.ndarray, cov: np.ndarray) -> float:
    """Per-step log-likelihood of X under a single Gaussian (no dynamics)."""
    D = mean.shape[0]
    sign, logdet = np.linalg.slogdet(cov)
    Cinv = np.linalg.inv(cov)
    total = 0.0
    for x in X:
        diff = x - mean
        total += -0.5 * (D * np.log(2 * np.pi) + logdet + diff @ Cinv @ diff)
    return float(total / len(X))


def identification_accuracy(score_matrix: np.ndarray) -> float:
    """Fraction of columns j whose max is on the diagonal (i == j)."""
    n = score_matrix.shape[0]
    correct = sum(int(np.argmax(score_matrix[:, j]) == j) for j in range(n))
    return correct / n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subjects", type=int, nargs="+", default=[1, 2, 3, 4, 5, 6, 7, 8])
    ap.add_argument("--hmm-states", type=int, default=3)
    ap.add_argument("--restarts", type=int, default=3)
    ap.add_argument("--session-a-run", type=int, default=4)
    ap.add_argument("--session-b-run", type=int, default=8)
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).parent / "results" / "a1_replicability.json")
    args = ap.parse_args()
    subs = args.subjects
    n = len(subs)

    print(f"Loading session A (run {args.session_a_run}) and B "
          f"(run {args.session_b_run}) for {n} subjects")
    covs_a = {s: load_run_covs(s, args.session_a_run) for s in subs}
    covs_b = {s: load_run_covs(s, args.session_b_run) for s in subs}

    # Single global reference from all session-A covariances pooled.
    pooled = [c for s in subs for c in covs_a[s]]
    print(f"Computing global AIRM reference from {len(pooled)} session-A covariances")
    ref = airm_frechet_mean(pooled, max_iter=50)

    def embed(covs):
        return np.array([spd_tangent_vector(ref, c) for c in covs])

    Xa = {s: embed(covs_a[s]) for s in subs}
    Xb = {s: embed(covs_b[s]) for s in subs}

    # Fit per-subject models on session A.
    print("Fitting per-subject HMM and static-Gaussian models on session A")
    hmms, statics = {}, {}
    for s in subs:
        hmms[s] = GaussianHMM(
            n_states=args.hmm_states, n_restarts=args.restarts,
            random_state=s, n_iter=60,
        ).fit(Xa[s])
        mean = Xa[s].mean(axis=0)
        cov = np.cov(Xa[s].T) + 1e-4 * np.eye(Xa[s].shape[1])
        statics[s] = (mean, cov)

    # Cross-score session B.
    L_hmm = np.zeros((n, n))
    L_static = np.zeros((n, n))
    for ii, si in enumerate(subs):
        for jj, sj in enumerate(subs):
            L_hmm[ii, jj] = hmms[si].score(Xb[sj]) / len(Xb[sj])
            m, c = statics[si]
            L_static[ii, jj] = static_gaussian_loglik(Xb[sj], m, c)

    acc_hmm = identification_accuracy(L_hmm)
    acc_static = identification_accuracy(L_static)
    chance = 1.0 / n

    # Binomial tail for each accuracy vs chance (n independent columns).
    from math import comb
    def binom_p(k, n, p):
        return sum(comb(n, i) * p**i * (1-p)**(n-i) for i in range(k, n+1))
    k_hmm = round(acc_hmm * n)
    k_static = round(acc_static * n)
    p_hmm = binom_p(k_hmm, n, chance)
    p_static = binom_p(k_static, n, chance)

    print()
    print(f"Cross-session identification (n={n}, chance={chance:.3f}):")
    print(f"  static-Gaussian (marginal only): {acc_static:.3f} "
          f"({k_static}/{n}), binomial p vs chance = {p_static:.4f}")
    print(f"  HMM (dynamics + geometry):       {acc_hmm:.3f} "
          f"({k_hmm}/{n}), binomial p vs chance = {p_hmm:.4f}")
    print()
    if acc_hmm > acc_static:
        verdict = ("HMM identifies BETTER than the marginal: dynamics add "
                   "subject-identifying information beyond static geometry. "
                   "A1 (dynamics replicate) SUPPORTED at this N.")
    elif acc_hmm == acc_static:
        verdict = ("HMM identifies NO better than the marginal: the "
                   "cross-session identity is carried by static geometry, "
                   "not dynamics. A1 (dynamics replicate) NOT supported: "
                   "the specificity ablation removes the effect.")
    else:
        verdict = ("HMM identifies WORSE than the marginal: the dynamics "
                   "model adds noise, not signal, for identification. A1 "
                   "NOT supported.")
    print("VERDICT:", verdict)
    print()
    print("NOTE: identification above chance by EITHER method only shows")
    print("subjects are distinguishable cross-session. The A1 dynamics")
    print("claim requires HMM to EXCEED the static baseline. With n=8 the")
    print("binomial is coarse (each step is 12.5 percent); treat small")
    print("HMM-minus-static gaps as suggestive, not conclusive.")

    result = {
        "n_subjects": n,
        "chance": chance,
        "hmm_states": args.hmm_states,
        "session_a_run": args.session_a_run,
        "session_b_run": args.session_b_run,
        "identification_accuracy_hmm": acc_hmm,
        "identification_accuracy_static": acc_static,
        "binomial_p_hmm": p_hmm,
        "binomial_p_static": p_static,
        "hmm_exceeds_static": bool(acc_hmm > acc_static),
        "score_matrix_hmm": L_hmm.tolist(),
        "score_matrix_static": L_static.tolist(),
        "verdict": verdict,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
