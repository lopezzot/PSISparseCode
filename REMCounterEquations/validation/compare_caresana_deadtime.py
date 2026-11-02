#!/usr/bin/env python3
"""Compare a Caresana-style discrete dead-time model with Fig. 4 of Caresana et al. (2014).

Requires: numpy, pandas, matplotlib.

The observed values are approximate manual digitizations of the raw square-marker
series in Fig. 4 (not machine-readable tabulated data). See README.md and the CSV
column digitization_note for the digitization convention and limitations.

Model:
    N0 = H_ref / c_cal
    w_i = integral of the normalized interaction-time density p(t) over fixed
          time bin [i*tau_d, (i+1)*tau_d]
    N_mean = sum_i [1 - exp(-N0*w_i)]
    H_pred = c_cal * N_mean

The fixed-bin approach follows the discrete Poisson-bin concept used in
Caresana et al. (2014), but replaces their time-distribution curve with the
single-exponential-kernel response to a finite rectangular source burst.
It is an approximation to counting-electronics dead time, not an exact
renewal-process model of an event-triggered non-paralyzable counter.
"""
from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "plots"
FIG_DIR = ROOT / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

TAIL_TIME_CONSTANTS = 16.0  # leaves an omitted exponential tail exp(-16) ~= 1.1e-7


def temporal_bin_weights(tb_us: float, tau_m_us: float, tau_d_us: float,
                         tail_constants: float = TAIL_TIME_CONSTANTS) -> np.ndarray:
    """Return probabilities w_i for dead-time-sized bins, using analytic integrals.

    The normalized response density for a rectangular source burst is
      p(t) = (1/Tb)*(1-exp(-t/tau_m)), 0 <= t <= Tb
      p(t) = (1/Tb)*(1-exp(-Tb/tau_m))*exp(-(t-Tb)/tau_m), t > Tb.
    All times are in microseconds. The density integrates to one over t>=0.
    """
    if tb_us <= 0 or tau_m_us <= 0 or tau_d_us <= 0:
        raise ValueError("Tb, tau_m and tau_d must all be positive")

    t_end = tb_us + tail_constants * tau_m_us
    n_bins = int(math.ceil(t_end / tau_d_us))
    edges = np.arange(n_bins + 1, dtype=float) * tau_d_us
    t0, t1 = edges[:-1], edges[1:]
    weights = np.zeros(n_bins, dtype=float)

    # Integral over the during-burst part: [t0,t1] intersected with [0,Tb].
    lo = np.maximum(t0, 0.0)
    hi = np.minimum(t1, tb_us)
    mask = hi > lo
    if np.any(mask):
        weights[mask] += (
            (hi[mask] - lo[mask])
            - tau_m_us * (np.exp(-lo[mask] / tau_m_us) - np.exp(-hi[mask] / tau_m_us))
        ) / tb_us

    # Integral over the post-burst exponential tail: [t0,t1] intersected with [Tb,infinity).
    lo_tail = np.maximum(t0, tb_us)
    hi_tail = t1
    mask_tail = hi_tail > lo_tail
    if np.any(mask_tail):
        g = 1.0 - math.exp(-tb_us / tau_m_us)
        weights[mask_tail] += (g * tau_m_us / tb_us) * (
            np.exp(-(lo_tail[mask_tail] - tb_us) / tau_m_us)
            - np.exp(-(hi_tail[mask_tail] - tb_us) / tau_m_us)
        )

    # Remove tiny roundoff artifacts and sanity-check the truncated normalization.
    weights = np.maximum(weights, 0.0)
    total = float(weights.sum())
    if not (0.999999 < total <= 1.000001):
        raise RuntimeError(
            f"Temporal weights sum to {total:.9f}; check parameters or integration formula"
        )
    return weights


def mean_registered_counts(h_ref_nsv: float, calibration_nsv_per_count: float,
                           weights: np.ndarray) -> float:
    """Expected counts using independent fixed bins of width tau_d."""
    if h_ref_nsv < 0 or calibration_nsv_per_count <= 0:
        raise ValueError("Dose must be non-negative and calibration coefficient positive")
    n0 = h_ref_nsv / calibration_nsv_per_count
    # -expm1(-x) accurately evaluates 1-exp(-x) for small x.
    return float(np.sum(-np.expm1(-n0 * weights)))


def predicted_measured_dose(h_ref_nsv: float, calibration_nsv_per_count: float,
                            weights: np.ndarray) -> tuple[float, float, float]:
    """Return (predicted measured dose, fraction registered, mean registered counts)."""
    n0 = h_ref_nsv / calibration_nsv_per_count
    n_mean = mean_registered_counts(h_ref_nsv, calibration_nsv_per_count, weights)
    if n0 == 0:
        return 0.0, 1.0, 0.0
    fraction = min(1.0, max(0.0, n_mean / n0))
    return calibration_nsv_per_count * n_mean, fraction, n_mean


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    params = pd.read_csv(DATA_DIR / "detector_parameters.csv")
    exp = pd.read_csv(DATA_DIR / "caresana_fig4_digitized.csv")
    if exp.empty or params.empty:
        raise RuntimeError("Input CSVs are empty")
    return params, exp


def make_detector_plot(detector: str, pdata: pd.Series, exp_data: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7.2, 5.6), constrained_layout=True)
    axis_max = max(exp_data.reference_dose_nsv.max() * 1.45, 10.0)
    ax.loglog([0.03, axis_max], [0.03, axis_max],
              linestyle="--", linewidth=1.2, color="0.5", label="Ideal linear response")

    colors = {1.0: "tab:blue", 10.0: "tab:orange", 40.0: "tab:green"}
    markers = {1.0: "o", 10.0: "s", 40.0: "^"}
    for tb in sorted(exp_data.burst_duration_us.unique()):
        dsub = exp_data[exp_data.burst_duration_us == tb].sort_values("reference_dose_nsv")
        ax.scatter(
            dsub.reference_dose_nsv,
            dsub.measured_dose_digitized_nsv,
            s=45,
            marker=markers.get(float(tb), "o"),
            color=colors.get(float(tb), None),
            edgecolor="black",
            linewidth=0.35,
            zorder=4,
            label=rf"Caresana et al., Fig. 4 (digitized), $T_b={tb:g}\,\mu$s",
        )

        # Evaluate a continuous model curve over the dose range represented by
        # the points for this burst duration (not merely through the point samples).
        hmin = max(0.01, float(dsub.reference_dose_nsv.min()) * 0.72)
        hmax = float(dsub.reference_dose_nsv.max()) * 1.25
        h_grid = np.logspace(np.log10(hmin), np.log10(hmax), 180)
        weights = temporal_bin_weights(float(tb), float(pdata.tau_m_us), float(pdata.tau_dead_us))
        h_model_grid = np.array([
            predicted_measured_dose(float(h), float(pdata.calibration_nsv_per_count), weights)[0]
            for h in h_grid
        ])
        ax.plot(
            h_grid,
            h_model_grid,
            color=colors.get(float(tb), None),
            linewidth=2.0,
            label=rf"Discrete-bin model, $T_b={tb:g}\,\mu$s",
        )

    ax.set_xlabel("Reference burst dose $H_b$ (nSv)")
    ax.set_ylabel("Measured-equivalent burst dose (nSv)")
    ax.grid(True, which="both", alpha=0.22)
    ax.set_xlim(0.05, axis_max)
    ax.set_ylim(0.05, axis_max)
    ax.legend(fontsize=8.2, loc="best", framealpha=0.92)

    info = (
        rf"$\tau_d={pdata.tau_dead_us:g}\,\mu\mathrm{{s}}$; "
        rf"$\tau_m={pdata.tau_m_us:g}\,\mu\mathrm{{s}}$ (assumed)" + "\n"
        + rf"$c_{{\mathrm{{cal}}}}={pdata.calibration_nsv_per_count:g}$ nSv/count"
    )
    ax.text(0.03, 0.97, info, transform=ax.transAxes, va="top", ha="left",
            fontsize=8.0, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85, edgecolor="0.8"))
    return fig


def main() -> None:
    params, exp = load_inputs()
    all_predictions = []

    for _, p in params.iterrows():
        detector = p["detector"]
        ed = exp[exp.detector == detector].copy().sort_values("setting")
        if ed.empty:
            print(f"WARNING: no data found for {detector}; skipping")
            continue

        # Cache weights for each source burst duration.
        weights_by_tb = {
            float(tb): temporal_bin_weights(
                float(tb), float(p.tau_m_us), float(p.tau_dead_us)
            )
            for tb in sorted(ed.burst_duration_us.unique())
        }

        local_rows = []
        for _, row in ed.iterrows():
            tb = float(row.burst_duration_us)
            weights = weights_by_tb[tb]
            h_model, frac, n_mean = predicted_measured_dose(
                float(row.reference_dose_nsv), float(p.calibration_nsv_per_count), weights
            )
            local_rows.append({
                "detector": detector,
                "setting": int(row.setting),
                "burst_charge_fc": float(row.burst_charge_fc),
                "burst_duration_us": tb,
                "reference_dose_nsv": float(row.reference_dose_nsv),
                "measured_dose_digitized_nsv": float(row.measured_dose_digitized_nsv),
                "predicted_measured_dose_nsv": h_model,
                "predicted_registered_fraction": frac,
                "predicted_loss_fraction": 1.0 - frac,
                "predicted_registered_counts": n_mean,
                "digitization_note": row.digitization_note,
            })
        pred_df = pd.DataFrame(local_rows)
        all_predictions.append(pred_df)

        fig = make_detector_plot(detector, p, ed)
        safe = detector.lower().replace(" ", "_").replace("-", "_")
        fig.savefig(FIG_DIR / f"fig_caresana_{safe}.png", dpi=300)
        plt.close(fig)
        print(f"Saved plot for {detector} in {FIG_DIR}")

    if not all_predictions:
        raise RuntimeError("No detector predictions were generated")
    predictions_df = pd.concat(all_predictions, ignore_index=True)
    predictions_df.to_csv(OUT_DIR / "model_predictions.csv", index=False)

    # Consolidated multi-page PDF.
    with PdfPages(OUT_DIR / "caresana_model_comparison.pdf") as pdf:
        for _, p in params.iterrows():
            detector = p["detector"]
            ed = exp[exp.detector == detector].copy().sort_values("setting")
            if ed.empty:
                continue
            fig = make_detector_plot(detector, p, ed)
            pdf.savefig(fig)
            plt.close(fig)

    print(f"Outputs written to: {OUT_DIR}")
    print("NOTE: Fig. 4 data points are approximate digitizations, not raw tabulated values. No half-response-dose estimates are displayed.")


if __name__ == "__main__":
    main()
