#!/usr/bin/env bash
# Fetch a subset of PhysioNet Sleep-EDF Expanded v1.0.0 sleep-cassette
# recordings (https://physionet.org/content/sleep-edfx/1.0.0/). Each subject
# has a PSG file (polysomnography; EEG Fpz-Cz and Pz-Oz at 100 Hz) and a
# hypnogram file (30-second sleep-stage annotations, Rechtschaffen & Kales).
#
# Used by experiments/sleep_transition_decoding/ to test whether the
# state-transition structure of sleep carries decodable signal beyond
# per-epoch features (ADR-018/ADR-019).
#
# License: Open Data Commons Attribution License v1.0. Cite Kemp et al. 2000
# (IEEE-BME 47(9)) and PhysioNet (Goldberger et al. 2000).
set -euo pipefail

OUT_DIR="data/raw/sleep_edfx"
BASE_URL="https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette"

# First-night cassette recordings SC4001..SC4014; missing ids are skipped.
SUBJECTS=()
for n in $(seq -w 1 14); do SUBJECTS+=("SC40${n}"); done

mkdir -p "$OUT_DIR"
echo "Fetching Sleep-EDF Expanded subset into $OUT_DIR ..."
for sub in "${SUBJECTS[@]}"; do
  for psg_suffix in "E0" "F0" "G0"; do
    url="${BASE_URL}/${sub}${psg_suffix}-PSG.edf"
    if curl -sfI "$url" >/dev/null 2>&1; then
      echo "  GET ${sub}${psg_suffix}-PSG.edf"
      curl -fsSL "$url?download" -o "$OUT_DIR/${sub}${psg_suffix}-PSG.edf"
      break
    fi
  done
  for hyp_suffix in "EC" "EH" "FC" "FH" "GC" "GH"; do
    url="${BASE_URL}/${sub}${hyp_suffix}-Hypnogram.edf"
    if curl -sfI "$url" >/dev/null 2>&1; then
      echo "  GET ${sub}${hyp_suffix}-Hypnogram.edf"
      curl -fsSL "$url?download" -o "$OUT_DIR/${sub}${hyp_suffix}-Hypnogram.edf"
      break
    fi
  done
done
echo "Done. See data/README.md for the PSG/hypnogram pairing convention."
