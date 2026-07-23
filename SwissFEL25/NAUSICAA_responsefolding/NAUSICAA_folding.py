import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# This is the low energy bin side for energy of the photon spectrum at position 4, i.e. the highest position of the NAUSICAA at the SwissFEL 2025 campaign.
photon_flux_bin_min = [9.9999997E-10,1.0964782E-09,1.2022645E-09,1.3182568E-09,1.4454400E-09,1.5848935E-09,1.7378012E-09,1.9054613E-09,2.0892970E-09,2.2908686E-09,2.5118878E-09,2.7542302E-09,3.0199536E-09,3.3113132E-09,3.6307830E-09,3.9810746E-09,4.3651625E-09,4.7863051E-09,5.2480797E-09,5.7544050E-09,6.3095800E-09,6.9183175E-09,7.5857844E-09,8.3176479E-09,9.1201207E-09,1.0000014E-08,1.0964798E-08,1.2022662E-08,1.3182588E-08,1.4454421E-08,1.5848958E-08,1.7378039E-08,1.9054641E-08,2.0892999E-08,2.2908720E-08,2.5118911E-08,2.7542342E-08,3.0199580E-08,3.3113182E-08,3.6307885E-08,3.9810804E-08,4.3651681E-08,4.7863118E-08,5.2480868E-08,5.7544135E-08,6.3095889E-08,6.9183272E-08,7.5857955E-08,8.3176602E-08,9.1201329E-08,1.0000028E-07,1.0964812E-07,1.2022679E-07,1.3182606E-07,1.4454442E-07,1.5848980E-07,1.7378063E-07,1.9054669E-07,2.0893029E-07,2.2908752E-07,2.5118950E-07,2.7542382E-07,3.0199621E-07,3.3113230E-07,3.6307938E-07,3.9810863E-07,4.3651744E-07,4.7863188E-07,5.2480942E-07,5.7544219E-07,6.3095985E-07,6.9183363E-07,7.5858065E-07,8.3176718E-07,9.1201463E-07,1.0000042E-06,1.0964828E-06,1.2022696E-06,1.3182624E-06,1.4454462E-06,1.5849004E-06,1.7378088E-06,1.9054694E-06,2.0893056E-06,2.2908785E-06,2.5118984E-06,2.7542419E-06,3.0199662E-06,3.3113279E-06,3.6307990E-06,3.9810920E-06,4.3651808E-06,4.7863259E-06,5.2481018E-06,5.7544294E-06,6.3096072E-06,6.9183475E-06,7.5858170E-06,8.3176838E-06,9.1201591E-06,1.0000056E-05,1.0964844E-05,1.2022713E-05,1.3182643E-05,1.4454482E-05,1.5849026E-05,1.7378110E-05,1.9054720E-05,2.0893089E-05,2.2908816E-05,2.5119019E-05,2.7542459E-05,3.0199708E-05,3.3113323E-05,3.6308040E-05,3.9810973E-05,4.3651868E-05,4.7863323E-05,5.2481097E-05,5.7544377E-05,6.3096166E-05,6.9183567E-05,7.5858276E-05,8.3176950E-05,9.1201720E-05,1.0000071E-04,1.0964860E-04,1.2022730E-04,1.3182664E-04,1.4454505E-04,1.5849050E-04,1.7378137E-04,1.9054749E-04,2.0893120E-04,2.2908850E-04,2.5119056E-04,2.7542500E-04,3.0199753E-04,3.3113372E-04,3.6308094E-04,3.9811034E-04,4.3651930E-04,4.7863391E-04,5.2481168E-04,5.7544466E-04,6.3096255E-04,6.9183676E-04,7.5858383E-04,8.3177071E-04,9.1201853E-04,1.0000085E-03,1.0964876E-03,1.2022748E-03,1.3182682E-03,1.4454524E-03,1.5849071E-03,1.7378164E-03,1.9054777E-03,2.0893149E-03,2.2908885E-03,2.5119095E-03,2.7542540E-03,3.0199795E-03,3.3113416E-03,3.6308144E-03,3.9811088E-03,4.3651992E-03,4.7863466E-03,5.2481247E-03,5.7544550E-03,6.3096345E-03,6.9183763E-03,7.5858496E-03,8.3177192E-03,9.1201989E-03,1.0000098E-02,1.0964892E-02,1.2022764E-02,1.3182701E-02,1.4454544E-02,1.5849093E-02,1.7378187E-02,1.9054806E-02,2.0893177E-02,2.2908917E-02,2.5119130E-02,2.7542580E-02,3.0199837E-02,3.3113468E-02,3.6308199E-02,3.9811146E-02,4.3652054E-02,4.7863536E-02,5.2481323E-02,5.7544626E-02,6.3096434E-02,6.9183864E-02,7.5858615E-02,8.3177313E-02,9.1202110E-02,0.1000011,0.1096491,0.1202278,0.1318272,0.1445457,0.1584912,0.1737821,0.1905483,0.2089321,0.2290895,0.2511916,0.2754261,0.3019988,0.3311351,0.3630825,0.3981120,0.4365212,0.4786360,0.5248140,0.5754471,0.6309653,0.6918396,0.7585871,0.8317743,0.9120225,1.000013,1.096492,1.202280,1.318274,1.445459,1.584914,1.737824,1.905486,2.089324,2.290898,2.511920,2.754266,3.019992,3.311356,3.630830,3.981126,4.365218,4.786367,5.248147,5.754479,6.309661,6.918406,7.585882,8.317756,9.120237]
photon_flux_bin_min = [x*1000 for x in photon_flux_bin_min] # convert GeV to MeV

# This is the upper energy bin side for energy of the photon spectrum at position 4, i.e. the highest position of the NAUSICAA at the SwissFEL 2025 campaign.
photon_flux_bin_max = [1.0964782E-09,1.2022645E-09,1.3182568E-09,1.4454400E-09,1.5848935E-09,1.7378012E-09,1.9054613E-09,2.0892970E-09,2.2908686E-09,2.5118878E-09,2.7542302E-09,3.0199536E-09,3.3113132E-09,3.6307830E-09,3.9810746E-09,4.3651625E-09,4.7863051E-09,5.2480797E-09,5.7544050E-09,6.3095800E-09,6.9183175E-09,7.5857844E-09,8.3176479E-09,9.1201207E-09,1.0000014E-08,1.0964798E-08,1.2022662E-08,1.3182588E-08,1.4454421E-08,1.5848958E-08,1.7378039E-08,1.9054641E-08,2.0892999E-08,2.2908720E-08,2.5118911E-08,2.7542342E-08,3.0199580E-08,3.3113182E-08,3.6307885E-08,3.9810804E-08,4.3651681E-08,4.7863118E-08,5.2480868E-08,5.7544135E-08,6.3095889E-08,6.9183272E-08,7.5857955E-08,8.3176602E-08,9.1201329E-08,1.0000028E-07,1.0964812E-07,1.2022679E-07,1.3182606E-07,1.4454442E-07,1.5848980E-07,1.7378063E-07,1.9054669E-07,2.0893029E-07,2.2908752E-07,2.5118950E-07,2.7542382E-07,3.0199621E-07,3.3113230E-07,3.6307938E-07,3.9810863E-07,4.3651744E-07,4.7863188E-07,5.2480942E-07,5.7544219E-07,6.3095985E-07,6.9183363E-07,7.5858065E-07,8.3176718E-07,9.1201463E-07,1.0000042E-06,1.0964828E-06,1.2022696E-06,1.3182624E-06,1.4454462E-06,1.5849004E-06,1.7378088E-06,1.9054694E-06,2.0893056E-06,2.2908785E-06,2.5118984E-06,2.7542419E-06,3.0199662E-06,3.3113279E-06,3.6307990E-06,3.9810920E-06,4.3651808E-06,4.7863259E-06,5.2481018E-06,5.7544294E-06,6.3096072E-06,6.9183475E-06,7.5858170E-06,8.3176838E-06,9.1201591E-06,1.0000056E-05,1.0964844E-05,1.2022713E-05,1.3182643E-05,1.4454482E-05,1.5849026E-05,1.7378110E-05,1.9054720E-05,2.0893089E-05,2.2908816E-05,2.5119019E-05,2.7542459E-05,3.0199708E-05,3.3113323E-05,3.6308040E-05,3.9810973E-05,4.3651868E-05,4.7863323E-05,5.2481097E-05,5.7544377E-05,6.3096166E-05,6.9183567E-05,7.5858276E-05,8.3176950E-05,9.1201720E-05,1.0000071E-04,1.0964860E-04,1.2022730E-04,1.3182664E-04,1.4454505E-04,1.5849050E-04,1.7378137E-04,1.9054749E-04,2.0893120E-04,2.2908850E-04,2.5119056E-04,2.7542500E-04,3.0199753E-04,3.3113372E-04,3.6308094E-04,3.9811034E-04,4.3651930E-04,4.7863391E-04,5.2481168E-04,5.7544466E-04,6.3096255E-04,6.9183676E-04,7.5858383E-04,8.3177071E-04,9.1201853E-04,1.0000085E-03,1.0964876E-03,1.2022748E-03,1.3182682E-03,1.4454524E-03,1.5849071E-03,1.7378164E-03,1.9054777E-03,2.0893149E-03,2.2908885E-03,2.5119095E-03,2.7542540E-03,3.0199795E-03,3.3113416E-03,3.6308144E-03,3.9811088E-03,4.3651992E-03,4.7863466E-03,5.2481247E-03,5.7544550E-03,6.3096345E-03,6.9183763E-03,7.5858496E-03,8.3177192E-03,9.1201989E-03,1.0000098E-02,1.0964892E-02,1.2022764E-02,1.3182701E-02,1.4454544E-02,1.5849093E-02,1.7378187E-02,1.9054806E-02,2.0893177E-02,2.2908917E-02,2.5119130E-02,2.7542580E-02,3.0199837E-02,3.3113468E-02,3.6308199E-02,3.9811146E-02,4.3652054E-02,4.7863536E-02,5.2481323E-02,5.7544626E-02,6.3096434E-02,6.9183864E-02,7.5858615E-02,8.3177313E-02,9.1202110E-02,0.1000011,0.1096491,0.1202278,0.1318272,0.1445457,0.1584912,0.1737821,0.1905483,0.2089321,0.2290895,0.2511916,0.2754261,0.3019988,0.3311351,0.3630825,0.3981120,0.4365212,0.4786360,0.5248140,0.5754471,0.6309653,0.6918396,0.7585871,0.8317743,0.9120225,1.000013,1.096492,1.202280,1.318274,1.445459,1.584914,1.737824,1.905486,2.089324,2.290898,2.511920,2.754266,3.019992,3.311356,3.630830,3.981126,4.365218,4.786367,5.248147,5.754479,6.309661,6.918406,7.585882,8.317756,9.120237,10.00014]
photon_flux_bin_max = [x*1000 for x in photon_flux_bin_max] # convert GeV to MeV

# This is the differential fluence of the photon (dN/dE) (Photons/GeVcm2) simulated with FLUKA in 2025, at position 4
photon_fluence_differential = [0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.1883284,0.3716128,0.8976647,1.799975,3.299529,5.018163,7.495956,9.668137,11.16610,12.64426,13.28309,12.83341,12.70221,11.88073,11.02692,10.10399,8.917664,7.971950,7.206193,6.434286,5.781934,5.348719,4.762899,4.229770,3.856040,3.647629,3.268050,2.891626,2.826470,4.333780,1.742298,1.574363,1.428251,1.302040,1.307094,1.134997,0.9559726,0.8514190,0.8148428,0.9046828,0.6957894,0.6287760,0.6708663,0.5429536,0.7485442,2.006321,0.3020775,0.3238368,0.2744371,0.2694189,0.7301329,0.2417044,0.2164314,0.1598161,0.5046489,0.1263389,0.1425179,0.1812102,9.0326257E-02,0.2274449,4.5358263E-02,1.6212652E-03,1.1986054E-03,1.4424808E-05,1.8272054E-06,2.4140493E-06,4.0123982E-06,3.2174893E-07,3.6244813E-07,1.4605443E-07,1.3205349E-07,1.2030080E-07,2.4611148E-07,5.7732997E-08,1.2192811E-07,2.1801219E-07,9.0455060E-08,8.3499714E-08,1.0970052E-07,4.0326551E-08,1.1914328E-07,2.2833403E-08,3.7643748E-08,3.7188485E-08,5.4477173E-08,3.2147899E-08,6.3326532E-08,2.6908317E-08,5.0689124E-09,1.9758023E-08,6.7522263E-09,7.9601223E-09,1.0459956E-08,4.9247011E-09,1.0853938E-08,2.6823501E-09,3.9961829E-09,0.000000,2.3011688E-10,1.4306879E-09,8.5427743E-10,2.9365121E-09,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000]

print("Entries for photon flux lower energggy bin side :", len(photon_flux_bin_min))
print("Entries for photon flux upper energy bin side :", len(photon_flux_bin_max))
print("Entries for photon flux differential fluence :",  len(photon_fluence_differential))

# --- Plot the photon fluence (particles/cm2) and photon differential fluence (particles/cm2MeV) ---

import matplotlib.pyplot as plt
import numpy as np

E_min = np.array(photon_flux_bin_min) # convert to numpy array
E_max = np.array(photon_flux_bin_max)
dN_dE = np.array(photon_fluence_differential) / 1000 # Convert GeV to MeV

dE = E_max - E_min # the width of each energy bin

fluence = dN_dE * dE # to get the fluence (photon/cm^2) I have to multiply my values for the bin width

E_center = np.sqrt(E_min * E_max) # the geometric mean for log-scaled bin centers

# The lethargy (E * dN/dE)
# Both E_center and the denominator of dN_dE are in MeV
lethargy = dN_dE * (E_center) # the lethargy 

fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot Photon Fluence on the primary Y-axis (left)
color1 = 'blue'
ax1.plot(E_center, fluence, label='Photon Fluence', color=color1, marker='.', linestyle='-')
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlabel('Energy (MeV)', fontsize=11)
ax1.set_ylabel('Fluence (particles/cm$^2$)', color=color1, fontsize=11)
ax1.tick_params(axis='y', labelcolor=color1)
ax1.grid(True, which="both", linestyle="--", alpha=0.5)

# Create a second Y-axis (ax2) sharing the same X-axis
ax2 = ax1.twinx()

# Plot Lethargy Fluence on the secondary Y-axis (right)
color2 = 'red'
ax2.plot(E_center, lethargy, label='Lethargy Fluence', color=color2, marker='x', linestyle='--', alpha=0.7)
ax2.set_yscale('log')
ax2.set_ylabel('Lethargy Fluence ($E dN/dE$)', color=color2, fontsize=11)
ax2.tick_params(axis='y', labelcolor=color2)

# Combine legends from both axes into a single box
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

plt.title('Photon Fluence and Lethargy vs Energy (2025)', fontsize=13, pad=10)
plt.tight_layout()
plt.savefig('photon_fluence_plot_pos4.png', dpi=300)

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
plt.close()

# Source Data 1: ICRP 74 Fluence-to-H*(10) for photons (ends at 10 MeV) ---
# Higher energies extension from Pelliccioni
#icru_energy_mev = np.array([
#    0.01, 0.015, 0.020, 0.030, 0.040, 0.050, 0.060, 0.080, 0.100, 0.150, 0.200, 0.300, 0.400, 0.500, 0.600, 0.800, 1, 1.5, 2, 3, 4, 5, 6, 8, 10,
#    20.0, 30.0, 40.0, 50.0, 60.0, 80.0, 100.0
#])

#icru_h10_psv_cm2 = np.array([
#    0.061, 0.83, 1.05, 0.81, 0.64, 0.55, 0.51, 0.53, 0.61, 0.89, 1.20, 1.80, 2.38, 2.93, 3.44, 4.38, 5.2, 6.9, 8.6, 11.1, 13.4, 15.5, 17.6, 21.6, 25.6,
#    27.5, 30.4, 32.2, 33.6, 34.6, 35.8, 36.8
#])

# --- ICRP 74 standard reference values for photons ---
icrp74_photons_energy_mev = np.array([
    1.00e-02, 1.50e-02, 2.00e-02, 3.00e-02, 4.00e-02, 5.00e-02, 6.00e-02,
    8.00e-02, 1.00e-01, 1.50e-01, 2.00e-01, 3.00e-01, 4.00e-01, 5.00e-01,
    6.00e-01, 8.00e-01, 1.00e+00, 1.50e+00, 2.00e+00, 3.00e+00, 4.00e+00,
    5.00e+00, 6.00e+00, 8.00e+00, 1.00e+01
])

icrp74_photons_h10_sv_cm2 = np.array([
    6.10e-14, 8.30e-13, 1.05e-12, 8.10e-13, 6.40e-13, 5.50e-13, 5.10e-13,
    5.30e-13, 6.10e-13, 8.90e-13, 1.20e-12, 1.80e-12, 2.38e-12, 2.93e-12,
    3.44e-12, 4.38e-12, 5.20e-12, 6.90e-12, 8.60e-12, 1.11e-11, 1.34e-11,
    1.55e-11, 1.76e-11, 2.16e-11, 2.56e-11
])

# --- Pelliccioni high-energy extension values for photons ---
pelliccioni_photons_energy_mev = np.array([
    1.0e-02, 1.5e-02, 2.0e-02, 3.0e-02, 4.0e-02, 5.0e-02, 6.0e-02, 8.0e-02,
    1.0e-01, 1.5e-01, 2.0e-01, 3.0e-01, 4.0e-01, 5.0e-01, 6.0e-01, 8.0e-01,
    1.0e+00, 1.5e+00, 2.0e+00, 3.0e+00, 4.0e+00, 5.0e+00, 6.0e+00, 8.0e+00,
    1.0e+01, 2.0e+01, 3.0e+01, 4.0e+01, 5.0e+01, 1.0e+02, 2.0e+02, 5.0e+02,
    1.0e+03, 2.0e+03, 5.0e+03, 1.0e+04
])

pelliccioni_photons_h10_sv_cm2 = np.array([
    8.33e-14, 8.52e-13, 1.05e-12, 0.80e-12, 0.62e-12, 0.52e-12, 0.51e-12,
    0.56e-12, 0.62e-12, 0.87e-12, 1.23e-12, 1.81e-12, 2.36e-12, 2.78e-12,
    3.46e-12, 4.29e-12, 5.18e-12, 6.92e-12, 8.25e-12, 1.04e-11, 1.07e-11,
    1.04e-11, 9.58e-12, 9.10e-12, 8.76e-12, 8.29e-12, 8.23e-12, 8.26e-12,
    8.64e-12, 9.00e-12, 1.02e-11, 1.18e-11, 1.17e-11, 1.15e-11, 1.33e-11,
    1.22e-11
])

# --- Merge datasets: ICRP74 up to 3 MeV, Pelliccioni above 3 MeV ---
# We used 3 MeV instead of 10 MeV to cross the two functions
# because at 3 MeV the KERMA approximation is still valid and the
# Pelliccioni method agrees well with the ICRP74 method.
# At 10 MeV this approximation is no longer valid and the two lines
# do not agree on the convertion factor.
# Filter ICRP74 data up to 3 MeV (inclusive)
icrp_mask_photons = icrp74_photons_energy_mev <= 3.0

# Filter Pelliccioni data strictly above 10.0 MeV
pell_mask_photons = pelliccioni_photons_energy_mev > 3.0

icru_photons_energy_mev = np.concatenate([
    icrp74_photons_energy_mev[icrp_mask_photons],
    pelliccioni_photons_energy_mev[pell_mask_photons]
])

icru_photons_h10_sv_cm2 = np.concatenate([
    icrp74_photons_h10_sv_cm2[icrp_mask_photons],
    pelliccioni_photons_h10_sv_cm2[pell_mask_photons]
])

# --- Convert Sv * cm^2 to pSv * cm^2 (1 Sv = 1e12 pSv) ---
icru_photons_h10_psv_cm2 = icru_photons_h10_sv_cm2 * 1e12

icru_energy_mev = icru_photons_energy_mev
icru_h10_psv_cm2 = icru_photons_h10_psv_cm2

# Log-log interpolation of ICRU conversion coefficients to match FLUKA bin centers
# Using log10 for both axes is standard for dosimetric data interpolation
interpolated_h10 = 10**np.interp(
    np.log10(E_center),
    np.log10(icru_energy_mev),
    np.log10(icru_h10_psv_cm2)
)

# Interpolate the NAUSICAA response over the FLUKA energy bin centers
interpolated_response = np.interp(
    np.log10(E_center),
    np.log10(nausicaa_energy_mev),
    nausicaa_response,
    left=0.0,
    right=nausicaa_response[-1]
)

# Calculate True Dose and Measured Dose (in pSv)
# Dose = Fluence (cm^-2) * h10 (pSv * cm^2)
true_dose_spectrum = fluence * interpolated_h10
measured_dose_spectrum = true_dose_spectrum * interpolated_response

total_true_dose = np.sum(true_dose_spectrum)
total_measured_dose = np.sum(measured_dose_spectrum)

# The correction factor is True Dose / Measured Dose
correction_factor = total_true_dose / total_measured_dose

print("\n==================================================")
print(f"Total True H*(10) Dose: {total_true_dose:.3e} pSv")
print(f"Total Measured NAUSICAA Dose: {total_measured_dose:.3e} pSv")
print(f"CALCULATED DOSE CORRECTION FACTOR: {correction_factor:.3f}")
print("==================================================")

# ==============================================================================
# --- PLOTTING: FLUKA FLUENCE + NAUSICAA RESPONSE (MASKED TO SPECTRUM RANGE) ---
# ==============================================================================

# Create a mask to filter NAUSICAA data so it only shows within the FLUKA spectrum range
plot_mask = (nausicaa_energy_mev >= E_center.min()) & (nausicaa_energy_mev <= E_center.max())
plot_nausicaa_E = nausicaa_energy_mev[plot_mask]
plot_nausicaa_resp = nausicaa_response[plot_mask]
fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, constrained_layout=True)

# Top Subplot: Particle Fluence from FLUKA
ax_top.plot(E_center, fluence, color='blue', marker='.', linestyle='-', linewidth=1.5, label='Neutron Fluence')
ax_top.set_yscale('log')
ax_top.set_ylabel('Fluence (cm$^{-2}$)', fontsize=11)
ax_top.grid(True, which="both", linestyle="--", alpha=0.5)
ax_top.set_title(f'FLUKA Photon Fluence vs NAUSICAA Response Comparison', fontsize=13, pad=10)
ax_top.legend(loc='upper right')

# Bottom Subplot: NAUSICAA Response
ax_bot.plot(plot_nausicaa_E, plot_nausicaa_resp, color='darkorange', marker='o', linestyle='-', linewidth=1.5, label='NAUSICAA Response')
ax_bot.axhline(1.0, color='gray', linestyle=':', alpha=0.7, label='Reference (1.0)')

ax_bot.set_xscale('log')
ax_bot.set_yscale('linear')
ax_bot.set_xlabel('Energy (MeV)', fontsize=11)
ax_bot.set_ylabel('Relative Response', fontsize=11)
ax_bot.grid(True, which="both", linestyle="--", alpha=0.5)
ax_bot.legend(loc='upper right')

# Ensure X-axis limits match the simulation exactly
ax_bot.set_xlim(E_center.min(), E_center.max())
ax_bot.set_ylim(-0.5, 12.0)

# Remove plt.tight_layout() as constrained_layout handles it now
plt.savefig('nausicaa_response_fluence_stacked.png', dpi=300)
plt.close()

# ==============================================================================
# --- PLOTTING: FLUKA FLUENCE + NAUSICAA RESPONSE + ICRU COEFFICIENTS ---
# ==============================================================================

# Create 3 subplots: Fluence (top), Response (mid), ICRU Conversion (bot)
fig, (ax_top, ax_mid, ax_bot) = plt.subplots(3, 1, figsize=(10, 11), sharex=True, constrained_layout=True)

# 1. Top Subplot: Particle Fluence from FLUKA
ax_top.plot(E_center, fluence, color='blue', marker='.', linestyle='-', linewidth=1.5, label='Photon Fluence')
ax_top.set_yscale('log')
ax_top.set_ylabel('Fluence (cm$^{-2}$)', fontsize=11)
ax_top.grid(True, which="both", linestyle="--", alpha=0.5)
ax_top.set_title('FLUKA Photon Fluence, NAUSICAA Response, and ICRU Coefficients', fontsize=13, pad=10)
ax_top.legend(loc='upper right')

# 2. Middle Subplot: NAUSICAA Response
plot_mask = (nausicaa_energy_mev >= E_center.min()) & (nausicaa_energy_mev <= E_center.max())
ax_mid.plot(nausicaa_energy_mev[plot_mask], nausicaa_response[plot_mask], color='darkorange', marker='o', linestyle='-', linewidth=1.5, label='NAUSICAA Response')
ax_mid.axhline(1.0, color='gray', linestyle=':', alpha=0.7, label='Reference (1.0)')
ax_mid.set_xscale('log')
ax_mid.set_yscale('linear')
ax_mid.set_ylabel('Relative Response', fontsize=11)
ax_mid.grid(True, which="both", linestyle="--", alpha=0.5)
ax_mid.legend(loc='upper right')

# 3. Bottom Subplot: ICRU Conversion Coefficients
ax_bot.plot(icru_energy_mev, icru_h10_psv_cm2, color='green', marker='s', linestyle='-', linewidth=1.5, label=r'H*(10)/$\Phi$ Conversion')
ax_bot.set_xscale('log')
ax_bot.set_yscale('log') # Log scale is necessary here as values span multiple orders of magnitude
ax_bot.set_xlabel('Energy (MeV)', fontsize=11)
ax_bot.set_ylabel(r'H*(10)/$\Phi$ (pSv cm$^2$)', fontsize=11)
ax_bot.grid(True, which="both", linestyle="--", alpha=0.5)
ax_bot.legend(loc='lower right')

# Set consistent X-axis limits for all plots
ax_bot.set_xlim(E_center.min(), E_center.max())

plt.savefig('photon_fluence_response_icru_stacked.png', dpi=300)
plt.close()
