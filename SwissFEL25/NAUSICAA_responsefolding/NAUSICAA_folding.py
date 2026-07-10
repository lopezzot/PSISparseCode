import numpy as np
import matplotlib.pyplot as plt

# --- Raw digitized X coordinates (linear extraction from plot) ---
raw_x = np.array([
    0.008668862836891502, 0.588758513855032, 1.008009489814776, 1.602890024788603,
    2.0217806610704354, 2.338741800696915, 2.6102535087129297, 3.0262805043779477,
    3.3471036374935736, 3.9372298083641324, 4.348337107603076, 4.94211754673669,
    5.365548462960208, 5.683609698426901, 5.94944711633839, 6.357124829701681,
    6.693241202676906, 7.273619125437375, 7.691214658523891, 8.286864624692317,
    8.70757815581535, 9.024261621925321, 9.289073131577345, 9.71686839719392,
    10.017077981087843
])

# --- NAUSICAA Relative Response (Y-axis) with negative values clamped to 0.0 ---
# These data come from ELSE Nuclear plot in a presentation for the SwissFEL 2025 measurement campaign
nausicaa_response = np.array([
    0.014057172471721389, 0.0008760844033367438, 0.0, 0.0,
    0.010841828934280302, 0.3432032205772884, 2.2689664451140232, 8.613057127814173,
    10.531866859063904, 6.963453342674441, 4.112547263758009, 2.0803818817780986,
    1.3849415313215818, 1.101536191245812, 0.9499417318538885, 0.8958588798692018,
    0.872544794792873, 0.8312004375870929, 0.8134500573579286, 0.8673781723570909,
    0.9497710660610307, 1.0013212376797076, 1.0268869734498072, 1.1307393839476876,
    1.2140948327233454
])

# --- Mathematical reconstruction of the logarithmic Energy axis (in MeV) ---
# The plot spans 3 decades: from 0.01 MeV (10^-2) to 10 MeV (10^1) over a 0-10 scale.
log_energy = -2.0 + (3.0 / 10.0) * raw_x
nausicaa_energy_mev = 10**log_energy

# ==============================================================================
# Plotting the Reconstructed NAUSICAA Energy Response
# ==============================================================================

fig, ax = plt.subplots(figsize=(8, 6))

# Plot the digitized data points and the interpolation line
ax.plot(nausicaa_energy_mev, nausicaa_response, color='#1f77b4', marker='o', 
        linestyle='-', linewidth=2, markersize=6, label='Digitized Data')

# Add a horizontal baseline at Y=1.0 (normalization reference at 600 keV)
ax.axhline(1.0, color='black', linestyle='-', linewidth=1.2, alpha=0.7, label='Reference to 600 keV')

# Set logarithmic scale for the X axis (Energy)
ax.set_xscale('log')

# Set plot limits to match the original image range
ax.set_xlim(0.01, 10.0)
ax.set_ylim(-0.5, 12.0)

# Labels and titles
ax.set_xlabel('E [MeV]', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('Relative Response to 600 keV', fontsize=12, fontweight='bold', labelpad=10)
ax.set_title('NAUSICAA Over-Response to Photons (60 - 300 keV)', fontsize=13, pad=15, fontweight='bold')

# Configure grid lines for log scale tracking
ax.grid(True, which="both", linestyle="--", alpha=0.5)

# Customize tick labels formatting if needed
ax.xaxis.set_major_formatter(plt.ScalarFormatter())
ax.set_xticks([0.01, 0.1, 1.0, 10.0])

ax.legend(loc='upper right', frameon=True, facecolor='#f7f7f7')

plt.tight_layout()
plt.savefig('nausicaa_fixed_response_plot.png', dpi=300)
plt.show()
