#!/usr/bin/env python3
"""Analytical figures for pulsed neutron fields in moderation-based REM counters.

Dependencies: numpy, matplotlib
Run: python rem_counter_pulsed_fields.py

All times in the calculation are expressed in seconds internally. Figures use
microseconds/kilohertz where appropriate. The model is an illustrative,
linear, single-exponential response model; it is not a detector-specific
Monte-Carlo model and does not simulate stochastic dead-time losses.
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

OUT = Path(__file__).resolve().parent / "rem_counter_figures"
OUT.mkdir(parents=True, exist_ok=True)

# Illustrative detector response parameters (based on the O(100 us) exponential
# time constants discussed in the 2023 review; adjust to a measured detector).
TAU_M_US = 100.0
TAU_M = TAU_M_US * 1e-6
TAU_DEAD_US = 5.0
TAU_DEAD = TAU_DEAD_US * 1e-6
K_INTERACTIONS_PER_NSV = 1.0

plt.rcParams.update({
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "legend.fontsize": 8,
    "figure.titlesize": 13,
    "savefig.dpi": 300,
    "axes.grid": True,
    "grid.alpha": 0.25,
})


def rect_response_density(t_s, width_s, tau_s):
    """Interaction-rate density per unit burst dose, lambda(t)/(k*H_b).

    A unit-dose rectangular source has q(t)=1/T for 0<=t<=T. The detector
    impulse response is h(t)=exp(-t/tau)/tau for t>=0. Their convolution is
    returned in units of 1/s and integrates to unity.
    """
    t = np.asarray(t_s, dtype=float)
    out = np.zeros_like(t)
    if width_s <= 0 or tau_s <= 0:
        raise ValueError("width_s and tau_s must be positive")
    during = (t >= 0.0) & (t <= width_s)
    after = t > width_s
    out[during] = (1.0 / width_s) * (1.0 - np.exp(-t[during] / tau_s))
    out[after] = ((1.0 / width_s) * (1.0 - np.exp(-width_s / tau_s))
                  * np.exp(-(t[after] - width_s) / tau_s))
    return out


def exponential_source_response_density(t_s, tau_m_s, tau_source_s):
    """Convolution of normalized exp source and exp detector kernels.

    g(t)=exp(-t/tau_source)/tau_source; h(t)=exp(-t/tau_m)/tau_m.
    For unequal time constants, (h*g)(t)=(exp(-t/tau_source)-
    exp(-t/tau_m))/(tau_source-tau_m), t>=0.
    """
    t = np.asarray(t_s, dtype=float)
    out = np.zeros_like(t)
    mask = t >= 0
    if np.isclose(tau_source_s, tau_m_s, rtol=1e-8, atol=0.0):
        out[mask] = (t[mask] / tau_m_s**2) * np.exp(-t[mask] / tau_m_s)
    else:
        out[mask] = (np.exp(-t[mask] / tau_source_s)
                     - np.exp(-t[mask] / tau_m_s)) / (tau_source_s - tau_m_s)
    return out


def periodic_impulse_response_normalized(x_s, period_s, tau_s):
    """Periodic steady-state rate divided by its cycle-average, for delta bursts."""
    phase = np.mod(np.asarray(x_s), period_s)
    return (period_s / tau_s) * np.exp(-phase / tau_s) / (-np.expm1(-period_s / tau_s))


def periodic_rectangular_ripple(width_s, period_s, tau_s):
    """Peak-to-peak / mean output ripple for periodic rectangular dose bursts.

    Valid for 0 < width <= period. The source is convolved with the normalized
    single-exponential response. The mean response is k*H_b/period.
    """
    if not (0 < width_s <= period_s):
        return np.nan
    a = -np.expm1(-width_s / tau_s)       # 1-exp(-T/tau)
    denom = -np.expm1(-period_s / tau_s)  # 1-exp(-P/tau)
    off_factor = -np.expm1(-(period_s - width_s) / tau_s)
    return (period_s / width_s) * a * off_factor / denom


def save(fig, filename):
    path = OUT / filename
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {path}")


# ---------------------------------------------------------------------------
# Figure 1: response to one rectangular burst of different widths.
# y = tau_m * lambda/(k H_b); an impulse has exp(-t/tau_m).
# ---------------------------------------------------------------------------
tau = TAU_M
u = np.linspace(0.0, 8.0, 6000)  # time / tau_m
t = u * tau
width_ratios = [0.01, 0.1, 1.0, 5.0]
fig, axs = plt.subplots(2, 2, figsize=(10.2, 6.8), sharex=True, sharey=True)
for ax, ratio in zip(axs.flat, width_ratios):
    T = ratio * tau
    density = rect_response_density(t, T, tau)
    ax.plot(u, tau * density, lw=2, label=r"$\tau_m\lambda(t)/(kH_b)$")
    ax.axvspan(0, ratio, color="tab:red", alpha=0.18, label="Source burst")
    ax.axvline(1.0, color="0.35", ls="--", lw=1, label=r"$t=\tau_m$")
    ax.set_title(rf"$T_b/\tau_m={ratio:g}$")
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 1.08)
    ax.set_xlabel(r"Time after burst, $t/\tau_m$")
    ax.set_ylabel("Normalized interaction-rate density")
    if ratio == 0.01:
        ax.legend(loc="upper right")
fig.suptitle("Single-burst response: source duration versus moderation/diffusion time")
fig.tight_layout()
save(fig, "fig1_single_burst_duration.png")


# ---------------------------------------------------------------------------
# Figure 2: generalized peak rate and allowed dose per burst vs T_b/tau_m.
# lambda_peak = k H_b/T_b * (1-exp(-T_b/tau_m)).
# H_lim/H_lim,short = x/(1-exp(-x)) under lambda_peak <= 1/(10 tau_dead).
# ---------------------------------------------------------------------------
x = np.logspace(-3, 2, 800)
peak_factor = -np.expm1(-x) / x
limit_factor = x / (-np.expm1(-x))
fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.2))
axs[0].semilogx(x, peak_factor, lw=2)
axs[0].axvline(1, color="0.35", ls="--", lw=1)
axs[0].axhline(1, color="0.5", ls=":", lw=1)
axs[0].set_xlabel(r"Burst duration ratio, $x=T_b/\tau_m$")
axs[0].set_ylabel(r"$\lambda_{\mathrm{peak}}/(kH_b/\tau_m)$")
axs[0].set_title("Peak-rate reduction for longer bursts")
axs[0].set_ylim(0, 1.05)
axs[1].loglog(x, limit_factor, lw=2)
axs[1].axvline(1, color="0.35", ls="--", lw=1)
axs[1].axhline(1, color="0.5", ls=":", lw=1)
axs[1].set_xlabel(r"Burst duration ratio, $x=T_b/\tau_m$")
axs[1].set_ylabel(r"$H_{b,\max}/H_{b,\max}(T_b\ll\tau_m)$")
axs[1].set_title("Dose-per-burst limit under a peak-rate criterion")
fig.suptitle("Analytical duration dependence for a single-exponential response")
fig.tight_layout()
save(fig, "fig2_peak_rate_and_dose_limit.png")


# ---------------------------------------------------------------------------
# Figure 3: prompt dose plus delayed exponential dose tail.
# q(t)=(1-eta)*uniform(Tp) + eta*exp(-t/Ts)/Ts.
# Output density = same weighted sum of the convolved density functions.
# ---------------------------------------------------------------------------
tau = TAU_M
Tp = 0.02 * tau
Ts = 3.0 * tau
t = np.linspace(0, 10 * tau, 5000)
u = t / tau
etas = [0.0, 0.25, 0.50, 0.75]
fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.2))
for eta in etas:
    # CDF of source dose delivery, with prompt dose approximated by a short rectangle.
    prompt_cdf = np.clip(t / Tp, 0.0, 1.0)
    tail_cdf = 1.0 - np.exp(-t / Ts)
    source_cdf = (1.0 - eta) * prompt_cdf + eta * tail_cdf
    axs[0].plot(u, source_cdf, lw=2, label=rf"$\eta={eta:.2f}$")

    output_density = ((1.0 - eta) * rect_response_density(t, Tp, tau)
                      + eta * exponential_source_response_density(t, tau, Ts))
    axs[1].plot(u, tau * output_density, lw=2, label=rf"$\eta={eta:.2f}$")

axs[0].set_title("Cumulative dose delivered by the source")
axs[0].set_xlabel(r"Time, $t/\tau_m$")
axs[0].set_ylabel(r"Cumulative fraction, $F_H(t)$")
axs[0].set_ylim(0, 1.02)
axs[0].legend(title="Delayed dose fraction")
axs[1].set_title("Interaction-time distribution at the detector")
axs[1].set_xlabel(r"Time, $t/\tau_m$")
axs[1].set_ylabel(r"$\tau_m\lambda(t)/(kH_b)$")
axs[1].legend(title="Delayed dose fraction")
fig.suptitle(rf"Prompt-plus-tail source model ($T_p/\tau_m={Tp/tau:.2f}$, $\tau_s/\tau_m={Ts/tau:.1f}$)")
fig.tight_layout()
save(fig, "fig3_delayed_dose_tail.png")


# ---------------------------------------------------------------------------
# Figure 4: periodic burst response at detector, for a periodic impulse train.
# lambda_ss(x)/mean = (P/tau)*exp(-x/tau)/(1-exp(-P/tau)), 0<=x<P.
# ---------------------------------------------------------------------------
tau = TAU_M
frequencies_khz = [2, 10, 50, 100]
period_max_us = 500.0
fig, axs = plt.subplots(4, 1, figsize=(10.2, 8.7), sharex=True)
for ax, f_khz in zip(axs, frequencies_khz):
    f = f_khz * 1e3
    P = 1.0 / f
    t = np.linspace(0, period_max_us * 1e-6, 15000, endpoint=False)
    normalized = periodic_impulse_response_normalized(t, P, tau)
    ax.plot(t * 1e6, normalized, lw=1.7, label=rf"$f={f_khz}$ kHz")
    ax.axhline(1.0, color="0.3", ls="--", lw=1, label="Cycle mean")
    # Source bursts are represented as narrow red ticks; plotted only if visually useful.
    burst_times = np.arange(0, period_max_us * 1e-6, P) * 1e6
    ax.vlines(burst_times, 0, 0.14, transform=ax.get_xaxis_transform(),
              color="tab:red", alpha=0.45, lw=1)
    ax.set_ylabel(r"$\lambda/\bar{\lambda}$")
    ax.set_ylim(0, max(1.25, min(5.6, float(np.max(normalized) * 1.08))))
    ax.text(0.99, 0.82, rf"$P/\tau_m={P/tau:.2g}$", transform=ax.transAxes,
            ha="right", va="top", fontsize=9)
    if f_khz == 2:
        ax.legend(loc="upper right", ncol=2)
axs[-1].set_xlabel("Time (µs)")
fig.suptitle(r"Pile-up of exponential detector responses from periodic bursts ($\tau_m=100$ µs)")
fig.tight_layout()
save(fig, "fig4_repetition_frequency_waveforms.png")


# ---------------------------------------------------------------------------
# Figure 5: output ripple versus repetition frequency for finite-width bursts.
# R_pp/mean has an exact closed form for a first-order exponential response.
# ---------------------------------------------------------------------------
tau = TAU_M
widths_us = [0.1, 1.0, 5.0, 10.0, 25.0, 50.0]
f_grid = np.logspace(np.log10(10.0), np.log10(200_000.0), 1000)
fig, ax = plt.subplots(figsize=(8.3, 5.0))
for width_us in widths_us:
    T = width_us * 1e-6
    ripples = []
    for f in f_grid:
        P = 1.0 / f
        ripples.append(periodic_rectangular_ripple(T, P, tau) if P >= T else np.nan)
    ax.loglog(f_grid / 1e3, ripples, lw=2, label=rf"$T_b={width_us:g}$ µs")
ax.axhline(0.10, color="tab:red", ls="--", lw=1.5,
           label="10% peak-to-peak / mean criterion")
ax.axvline(1.0 / (0.10 * tau) / 1e3, color="0.25", ls=":", lw=1.5,
           label="Impulse approximation: 10% criterion")
ax.set_xlabel("Repetition frequency (kHz)")
ax.set_ylabel(r"Relative ripple $(\lambda_{\max}-\lambda_{\min})/\bar{\lambda}$")
ax.set_title(r"A quantitative, threshold-dependent definition of quasi-stationarity ($\tau_m=100$ µs)")
ax.set_ylim(1e-3, 1e3)
ax.legend(loc="best")
fig.tight_layout()
save(fig, "fig5_ripple_vs_frequency.png")


# ---------------------------------------------------------------------------
# Figure 6: dead-time operating criterion as a normalized burst-dose limit.
# Hmax = T_b / [10*k*tau_dead*(1-exp(-T_b/tau_m))].
# Normalized by the short-burst limit tau_m/(10*k*tau_dead).
# This is an overload criterion, NOT a universal dead-time correction formula.
# ---------------------------------------------------------------------------
x = np.logspace(-3, 2, 800)
normalized_hmax = x / (-np.expm1(-x))
fig, ax = plt.subplots(figsize=(8.3, 4.8))
ax.semilogx(x, normalized_hmax, lw=2.2)
ax.axhline(1.0, color="0.4", ls=":", lw=1.2)
ax.axvline(1.0, color="0.4", ls="--", lw=1.2)
ax.set_xlabel(r"Burst duration ratio, $T_b/\tau_m$")
ax.set_ylabel(r"$H_{b,\max}/[\tau_m/(10k\tau_d)]$")
ax.set_title("Illustrative dead-time margin versus burst duration")
ax.annotate("Short-burst limit\nfixed allowed dose per burst", xy=(0.002, 1.02),
            xytext=(0.01, 2.2), textcoords="data",
            arrowprops={"arrowstyle": "->", "lw": 1.0}, fontsize=9)
ax.annotate(r"For $T_b\gg\tau_m$, $H_{b,\max}\propto T_b$",
            xy=(20, 20.5), xytext=(1.0, 8.0), textcoords="data",
            arrowprops={"arrowstyle": "->", "lw": 1.0}, fontsize=9)
fig.tight_layout()
save(fig, "fig6_dead_time_margin.png")

print("\nAll figures generated. Parameters are at the top of this file.")
print(f"Illustrative exponential-response time constant: {TAU_M_US:g} µs")
print(f"Illustrative electronics dead time: {TAU_DEAD_US:g} µs")
print("Reminder: 2014's example uses TDT=500 µs in its average-rate criterion; do not equate that automatically to the ~100 µs exponential decay constant reported in the 2023 review.")
