import numpy as np
import matplotlib.pyplot as plt

# Detector and irradiation parameters based on the WENDI-II row of the manuscript.
tau_d_us = 1.8
tau_m_us = 70.0
c_cal_nSv_per_count = 0.33
T_b_us = 10.0
burst_doses_nSv = [0.5, 1.0, 2.0]

# Enforce the synchronization condition P = N_P * tau_d and T_b < P.
nP_min = int(np.floor(T_b_us / tau_d_us)) + 1
nP_dense = np.arange(nP_min, 151, dtype=int)
nP_log = np.unique(np.round(np.geomspace(151, 100000, 150)).astype(int))
nP_values = np.unique(np.concatenate([nP_dense, nP_log]))

# Truncate only the negligible exponential tail, consistently with the manuscript.
n_bins_tail = int(np.ceil((T_b_us + 16.0 * tau_m_us) / tau_d_us))
J = int(np.floor(T_b_us / tau_d_us))
delta = T_b_us - J * tau_d_us
rho = np.exp(-tau_d_us / tau_m_us)
exp_T = np.exp(-T_b_us / tau_m_us)

def periodic_counting_loss_percent(H_b_nSv, N_P):
    # Calculate the periodic parameters.
    period_us = N_P * tau_d_us
    beta = (1.0 - exp_T) / (1.0 - np.exp(-period_us / tau_m_us))
    alpha = beta * np.exp(-(period_us - T_b_us) / tau_m_us)

    # Use all bins for short periods and truncate the negligible tail for long periods.
    n_bins = min(N_P, n_bins_tail)
    i = np.arange(n_bins)
    w = np.empty(n_bins, dtype=float)

    # Bins fully contained within the burst.
    inside = i < J
    w[inside] = (
        tau_d_us / T_b_us
        - tau_m_us / T_b_us
        * (1.0 - alpha) * (1.0 - rho) * rho ** i[inside]
    )

    # Bin containing the end of the burst.
    if J < n_bins:
        w[J] = (
            delta
            - (1.0 - alpha) * tau_m_us * (rho ** J - exp_T)
            + beta * tau_m_us
            * (1.0 - np.exp(-(tau_d_us - delta) / tau_m_us))
        ) / T_b_us

    # Bins in the exponential decay interval.
    decay = i > J
    w[decay] = (
        beta * tau_m_us / T_b_us
        * (1.0 - rho)
        * np.exp(-(i[decay] * tau_d_us - T_b_us) / tau_m_us)
    )

    # Evaluate the expected registered counts using the discrete Poisson model.
    N0 = H_b_nSv / c_cal_nSv_per_count
    N_mean = np.sum(-np.expm1(-N0 * w))
    return 100.0 * (1.0 - N_mean / N0)

# Convert the allowed synchronized frequencies to kHz.
frequencies_kHz = 1000.0 / (nP_values * tau_d_us)
order = np.argsort(frequencies_kHz)
frequencies_kHz = frequencies_kHz[order]
nP_values = nP_values[order]

fig, ax = plt.subplots(figsize=(8.2, 5.4), constrained_layout=True)

for H_b in burst_doses_nSv:
    losses = np.array([
        periodic_counting_loss_percent(H_b, int(N_P))
        for N_P in nP_values
    ])
    ax.plot(
        frequencies_kHz, losses,
        marker="o", markersize=2.5, linewidth=1.5,
        label=fr"$H_b = {H_b:g}\,\mathrm{{nSv}}$"
    )

# Mark the characteristic frequency for which the period equals tau_m.
f_characteristic_kHz = 1000.0 / tau_m_us
ax.axvline(
    f_characteristic_kHz, linestyle="--", linewidth=1.0,
    label=fr"$P=\tau_m$ ({f_characteristic_kHz:.1f} kHz)"
)

ax.set_xscale("log")
ax.set_xlabel("Burst repetition frequency, $f$ (kHz)")
ax.set_ylabel("Expected counting loss per burst, $L_{\\mathrm{per}}$ (%)")
ax.set_title(
    "Periodic counting losses for a WENDI-II-like detector\n"
    fr"$T_b={T_b_us:g}\,\mu$s, "
    fr"$\tau_d={tau_d_us:g}\,\mu$s, "
    fr"$\tau_m={tau_m_us:g}\,\mu$s"
)
ax.grid(True, which="both", alpha=0.25)
ax.legend(title="Burst dose")
ax.set_xlim(frequencies_kHz.min(), frequencies_kHz.max())
ax.set_ylim(bottom=0)
plt.show()
