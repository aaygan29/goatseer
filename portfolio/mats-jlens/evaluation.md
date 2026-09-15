# mats-jlens: evaluation

- External home: github.com/aaygan29/mats_task (confirmed via `gh repo view`: private, default
  branch `main`, pushed 2026-08-15). No local checkout found on disk this pass.
- Status: active
- Last scored: 2026-09-03
- Next re-score due: 2026-09-17

## One-line claim

Exploratory: on Qwen3-4B multi-hop recall, the J-Lens direction is a better detector of
the answer than logit-lens or a diff-of-means probe (MRR 0.60 vs 0.46), but not a better
causal writer under matched-norm steering (paired permutation p=0.998); the causal
mediation that does exist is mostly token-injection rather than genuine circuit control.

## Gate scores

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | pass | Held-out bake corpus separates the lens-fitting data from the evaluation data; Modal HF-cache pinned deps documented. |
| G2 seed variance (n>=5)      | partial | A multi-seed random-direction control is reported, but the headline detection/causal metrics themselves (n=17 items) are not reported as a >=5-seed sweep of the point estimate. |
| G3 specification robustness  | pass | A full alpha (steering-strength) curve is reported (fig5), not a single cherry-picked alpha; the readout layer L* is chosen from baseline lenses only, avoiding circularity with the tested lens. |
| G4 specificity ablation      | pass | Answer-swap-dominance, token-push, and random-direction controls are all run; the honest finding is that steering mostly writes the entity token (token-push 0.21 far exceeds the answer effect), which is exactly the specificity check working as intended. |
| G5 confound control          | partial | The pair-linearity confound (Neel Nanda's own objection: intermediate/answer pairs may be linearly related in unembedding space) is explicitly controlled via a low-/high-cosine split: the confound most relevant to this design. The generic LLM-addendum trio (prompt length, formatting, token position) is not separately itemized. |
| G6 mechanism/necessity       | partial | A genuine intervention (matched-norm causal steering with controls) is run, but the result is an honest null on necessity: C3 (confound-controlled causal effect) is inconclusive (CI includes 0). |
| G7 calibration                | unscored (no evidence available) | |
| G8 external validity          | unscored (no evidence available; single model, Qwen3-4B only) | |
| G9 measurement reliability    | unscored (no evidence available) | |
| G10 reproducibility            | partial | Checkpointed orchestrator with a labeled `_smoke_qwen3-0.6B` result explicitly marked "NOT-a-result"; `configs/main.yaml` targets the real 4B run on Modal, but no stated end-to-end timing or fresh-venv reproduce target was found. |
| G11 ethics/safety              | pass | Public model, mechanistic-interpretability research, no PHI or targeted-individual content. |
| G12 analytic integrity         | pass | L* chosen a priori from baseline lenses only, alpha fixed a priori with the full curve reported alongside, and a smoke sanity-gate (random control near 0) is checked before trusting real results; an earlier metric/alpha bug is quarantined and documented (`results/_run1_*`) rather than silently dropped. |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | n/a | Not an fMRI-grounded claim. |
| G-fMRI.2 sign-concordance binomial | n/a | |
| G-fMRI.3 group-level significance  | n/a | |

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | n/a | Mechanistic-interpretability harness, not a decision-answering instrument. |
| H2 calibrated confidence       | n/a | |
| H3 loyalty vector disclosure   | n/a | |

## Contribution to NEUROSPINE

Tuple field(s) this project could feed: `sparse_circuit_id` (this is the most direct fit
in the whole portfolio: a DreamerV3-style handle on the mechanism is exactly what J-Lens
vs logit-lens vs probe is testing). The honest finding (reader, not writer) should be
encoded as a caveat on that field, not hidden.

## Open action items

- [ ] Fit a properly-trained tuned-lens baseline (the current one is undertrained on a
  30-sentence corpus and does not cleanly settle the network-aware-baseline critique);
  direct fix for the residual limitation flagged in the memory itself.
- [ ] Add more low-linearity-similarity items the 4B model can actually solve, to make C3
  (confound-controlled causal effect) conclusive instead of CI-includes-0.
- [ ] Replicate the detection-vs-causal-writer dissociation on a second model to establish
  G8; currently a single-model (Qwen3-4B) result.
