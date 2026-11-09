#!/usr/bin/env python3
"""Monte Carlo comparison of fixed-bin and event-driven dead-time models.

The script compares:
1. The analytical fixed-bin Poisson counting-loss model.
2. A Monte Carlo implementation of the same fixed-bin model.
3. An event-driven non-paralyzable dead-time Monte Carlo model.

Both Monte Carlo models process the same simulated interaction times in each
realization. Interaction times are sampled from the convolution of a uniform
rectangular source burst and a single-exponential detector response.

Required packages: numpy, matplotlib, numba.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from numba import njit


# -----------------------------------------------------------------------------
# Model parameters (WENDI-II-like values used in the manuscript)
# -----------------------------------------------------------------------------
TAU_M_US = 70.0       # Exponential detector-response time constant [us]
TAU_D_US = 1.8        # Electronic dead time [us]
C_CAL_NSV = 0.33      # Calibration coefficient [nSv/count]
T_B_US = 10.0         # Rectangular source-burst duration [us]

# Monte Carlo settings
N_REALIZATIONS = 60_000
RANDOM_SEED = 20261109
N_DOSE_POINTS = 16
DOSE_MIN_NSV = 0.2
DOSE_MAX_NSV = 30.0
TAIL_CONSTANTS = 18.0

# Output files are written next to this script.
OUTPUT_DIR = Path(__file__).resolve().parent
FIGURE_PDF = OUTPUT_DIR / "isolated_burst_count_loss_mc.pdf"
FIGURE_PNG = OUTPUT_DIR / "isolated_burst_count_loss_mc.png"
DATA_CSV = OUTPUT_DIR / "isolated_burst_count_loss_mc.csv"


def interaction_cdf(time_us, burst_duration_us, tau_m_us):
    """Return the CDF of the normalized interaction-time distribution."""
    time_us = np.asarray(time_us, dtype=float)
    cdf = np.zeros_like(time_us)

    during_burst = (time_us > 0.0) & (time_us <= burst_duration_us)
    t = time_us[during_burst]
    cdf[during_burst] = (
        t - tau_m_us * (1.0 - np.exp(-t / tau_m_us))
    ) / burst_duration_us

    after_burst = time_us > burst_duration_us
    t = time_us[after_burst]
    cdf_at_burst_end = (
        burst_duration_us
        - tau_m_us * (1.0 - np.exp(-burst_duration_us / tau_m_us))
    ) / burst_duration_us
    cdf[after_burst] = cdf_at_burst_end + (
        tau_m_us
        / burst_duration_us
        * (1.0 - np.exp(-burst_duration_us / tau_m_us))
        * (1.0 - np.exp(-(t - burst_duration_us) / tau_m_us))
    )

    return cdf


def isolated_bin_weights(
    burst_duration_us,
    tau_m_us,
    tau_d_us,
    tail_constants=TAIL_CONSTANTS,
):
    """Calculate fixed-bin interaction probabilities by CDF integration."""
    end_time_us = burst_duration_us + tail_constants * tau_m_us
    n_bins = int(np.ceil(end_time_us / tau_d_us))
    bin_edges_us = np.arange(n_bins + 1, dtype=float) * tau_d_us
    return np.diff(interaction_cdf(bin_edges_us, burst_duration_us, tau_m_us))


def analytical_fixed_bin_loss(expected_interactions, bin_weights):
    """Calculate the analytical fractional loss for the fixed-bin model."""
    # expm1 improves numerical accuracy when the bin occupancy is small.
    expected_registered = np.sum(-np.expm1(-expected_interactions * bin_weights))
    return 1.0 - expected_registered / expected_interactions


@njit
def _simulate_paired_models_numba(
    n_realizations,
    expected_interactions,
    burst_duration_us,
    tau_m_us,
    tau_d_us,
    seed,
):
    """Process the same Poisson interaction events with both dead-time models."""
    np.random.seed(seed)

    sum_lost_fixed = 0.0
    sum_lost_fixed_sq = 0.0
    sum_lost_np = 0.0
    sum_lost_np_sq = 0.0

    for _ in range(n_realizations):
        # A Poisson number of events with iid times sampled from the normalized
        # interaction-time density is an inhomogeneous Poisson point process.
        n_events = np.random.poisson(expected_interactions)
        event_times = np.empty(n_events, dtype=np.float64)

        for j in range(n_events):
            source_time = np.random.random() * burst_duration_us
            u = np.random.random()
            if u < 1.0e-15:
                u = 1.0e-15
            moderation_delay = -tau_m_us * np.log(u)
            event_times[j] = source_time + moderation_delay

        event_times.sort()

        # Model 1: fixed bins anchored to the source-burst start.
        n_registered_fixed = 0
        previous_bin = -1

        # Model 2: event-driven non-paralyzable electronics.
        n_registered_np = 0
        last_registered_time = -1.0e30

        for j in range(n_events):
            event_time = event_times[j]

            # Fixed-bin model: retain at most one event in each predefined bin.
            bin_index = int(event_time / tau_d_us)
            if bin_index != previous_bin:
                n_registered_fixed += 1
                previous_bin = bin_index

            # Non-paralyzable model: dead time starts after each registered event.
            if event_time - last_registered_time >= tau_d_us:
                n_registered_np += 1
                last_registered_time = event_time

        lost_fixed = n_events - n_registered_fixed
        lost_np = n_events - n_registered_np

        sum_lost_fixed += lost_fixed
        sum_lost_fixed_sq += lost_fixed * lost_fixed
        sum_lost_np += lost_np
        sum_lost_np_sq += lost_np * lost_np

    # Return fractional losses and standard errors across realizations.
    mean_lost_fixed = sum_lost_fixed / n_realizations
    mean_lost_np = sum_lost_np / n_realizations

    variance_fixed = (
        sum_lost_fixed_sq - n_realizations * mean_lost_fixed**2
    ) / (n_realizations - 1)
    variance_np = (
        sum_lost_np_sq - n_realizations * mean_lost_np**2
    ) / (n_realizations - 1)

    variance_fixed = max(variance_fixed, 0.0)
    variance_np = max(variance_np, 0.0)

    loss_fixed = mean_lost_fixed / expected_interactions
    loss_np = mean_lost_np / expected_interactions
    se_fixed = np.sqrt(variance_fixed / n_realizations) / expected_interactions
    se_np = np.sqrt(variance_np / n_realizations) / expected_interactions

    return loss_fixed, se_fixed, loss_np, se_np


def simulate_paired_models(
    n_realizations,
    expected_interactions,
    burst_duration_us,
    tau_m_us,
    tau_d_us,
    seed,
):
    """Run paired Monte Carlo simulations with basic input validation."""
    if n_realizations < 2:
        raise ValueError("At least two Monte Carlo realizations are required.")
    if expected_interactions <= 0.0:
        raise ValueError("The expected number of interactions must be positive.")
    if min(burst_duration_us, tau_m_us, tau_d_us) <= 0.0:
        raise ValueError("All time parameters must be positive.")

    return _simulate_paired_models_numba(
        n_realizations,
        expected_interactions,
        burst_duration_us,
        tau_m_us,
        tau_d_us,
        seed,
    )


def main():
    """Run the dose scan, create the figure, and save the numerical data."""
    doses_nsv = np.geomspace(DOSE_MIN_NSV, DOSE_MAX_NSV, N_DOSE_POINTS)
    expected_interactions = doses_nsv / C_CAL_NSV

    bin_weights = isolated_bin_weights(T_B_US, TAU_M_US, TAU_D_US)

    analytical_loss = np.array(
        [analytical_fixed_bin_loss(n0, bin_weights) for n0 in expected_interactions]
    )

    mc_fixed_loss = np.empty_like(doses_nsv)
    mc_fixed_se = np.empty_like(doses_nsv)
    mc_np_loss = np.empty_like(doses_nsv)
    mc_np_se = np.empty_like(doses_nsv)

    for index, n0 in enumerate(expected_interactions):
        (
            mc_fixed_loss[index],
            mc_fixed_se[index],
            mc_np_loss[index],
            mc_np_se[index],
        ) = simulate_paired_models(
            N_REALIZATIONS,
            float(n0),
            T_B_US,
            TAU_M_US,
            TAU_D_US,
            RANDOM_SEED + index,
        )

        print(
            f"H_b={doses_nsv[index]:6.3f} nSv | "
            f"fixed-bin MC={mc_fixed_loss[index]:.5f} "
            f"+/- {mc_fixed_se[index]:.5f} | "
            f"non-paralyzable MC={mc_np_loss[index]:.5f} "
            f"+/- {mc_np_se[index]:.5f}"
        )

    # Create a single-panel figure for the isolated-burst comparison.
    fig, ax = plt.subplots(figsize=(6.6, 4.6))

    ax.plot(
        doses_nsv,
        analytical_loss,
        linestyle="-",
        linewidth=1.8,
        label="Analytical fixed-bin model",
    )
    ax.errorbar(
        doses_nsv,
        mc_fixed_loss,
        yerr=mc_fixed_se,
        linestyle="none",
        marker="o",
        markersize=4.5,
        capsize=2,
        label="Fixed-bin Monte Carlo",
    )
    ax.errorbar(
        doses_nsv,
        mc_np_loss,
        yerr=mc_np_se,
        linestyle="none",
        marker="s",
        markersize=4.5,
        capsize=2,
        label="Event-driven non-paralyzable MC",
    )

    ax.set_xscale("log")
    ax.set_xlabel(r"Dose per burst $H_b$ (nSv)")
    ax.set_ylabel(r"Fractional counting loss $L$")
    ax.set_title(
        rf"Isolated rectangular burst: $T_b={T_B_US:g}\,\mu$s, "
        rf"$\tau_m={TAU_M_US:g}\,\mu$s, $\tau_d={TAU_D_US:g}\,\mu$s"
    )
    ax.set_xlim(DOSE_MIN_NSV * 0.9, DOSE_MAX_NSV * 1.12)
    ax.set_ylim(bottom=0.0)
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(frameon=False, fontsize=8.5)

    fig.tight_layout()
    fig.savefig(FIGURE_PDF, bbox_inches="tight")
    fig.savefig(FIGURE_PNG, dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Save the data used to generate the figure.
    output_data = np.column_stack(
        [
            doses_nsv,
            expected_interactions,
            analytical_loss,
            mc_fixed_loss,
            mc_fixed_se,
            mc_np_loss,
            mc_np_se,
        ]
    )
    np.savetxt(
        DATA_CSV,
        output_data,
        delimiter=",",
        header=(
            "burst_dose_nSv,expected_interactions,"
            "analytical_fixed_bin_loss,mc_fixed_bin_loss,mc_fixed_bin_SE,"
            "mc_nonparalyzable_loss,mc_nonparalyzable_SE"
        ),
        comments="",
    )

    print(f"\nFigure saved to: {FIGURE_PDF}")
    print(f"Figure saved to: {FIGURE_PNG}")
    print(f"Data saved to:   {DATA_CSV}")


if __name__ == "__main__":
    main()
