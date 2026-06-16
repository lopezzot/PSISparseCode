'''
This code was created to calculate the correction of the WENDI-2 photon detector dose measurement when used in the SwissFel neutron radiation environment.
Specifically the photon fluence was calculated with FLUKA based on the 2025 measurement campaign at the PSI SwissFel.
'''
# This is the lower side of the energy bins for the photon flux simulated with FLUKA in 2025 at SwissFEL
photon_flux_bin_min = [9.9999997E-10, 1.0964782E-09, 1.2022645E-09, 1.3182568E-09, 1.4454400E-09, 1.5848935E-09, 1.7378012E-09, 1.9054613E-09, 2.0892970E-09, 2.2908686E-09, 2.5118878E-09, 2.7542302E-09, 3.0199536E-09, 3.3113132E-09, 3.6307830E-09, 3.9810746E-09, 4.3651625E-09, 4.7863051E-09, 5.2480797E-09, 5.7544050E-09, 6.3095800E-09, 6.9183175E-09, 7.5857844E-09, 8.3176479E-09, 9.1201207E-09, 1.0000014E-08, 1.0964798E-08, 1.2022662E-08, 1.3182588E-08, 1.4454421E-08, 1.5848958E-08, 1.7378039E-08, 1.9054641E-08, 2.0892999E-08, 2.2908720E-08, 2.5118911E-08, 2.7542342E-08, 3.0199580E-08, 3.3113182E-08, 3.6307885E-08, 3.9810804E-08, 4.3651681E-08, 4.7863118E-08, 5.2480868E-08, 5.7544135E-08, 6.3095889E-08, 6.9183272E-08, 7.5857955E-08, 8.3176602E-08, 9.1201329E-08, 1.0000028E-07, 1.0964812E-07, 1.2022679E-07, 1.3182606E-07, 1.4454442E-07, 1.5848980E-07, 1.7378063E-07, 1.9054669E-07, 2.0893029E-07, 2.2908752E-07, 2.5118950E-07, 2.7542382E-07, 3.0199621E-07, 3.3113230E-07, 3.6307938E-07, 3.9810863E-07, 4.3651744E-07, 4.7863188E-07, 5.2480942E-07, 5.7544219E-07, 6.3095985E-07, 6.9183363E-07, 7.5858065E-07, 8.3176718E-07, 9.1201463E-07, 1.0000042E-06, 1.0964828E-06, 1.2022696E-06, 1.3182624E-06, 1.4454462E-06, 1.5849004E-06, 1.7378088E-06, 1.9054694E-06, 2.0893056E-06, 2.2908785E-06, 2.5118984E-06, 2.7542419E-06, 3.0199662E-06, 3.3113279E-06, 3.6307990E-06, 3.9810920E-06, 4.3651808E-06, 4.7863259E-06, 5.2481018E-06, 5.7544294E-06, 6.3096072E-06, 6.9183475E-06, 7.5858170E-06, 8.3176838E-06, 9.1201591E-06, 1.0000056E-05, 1.0964844E-05, 1.2022713E-05, 1.3182643E-05, 1.4454482E-05, 1.5849026E-05, 1.7378110E-05, 1.9054720E-05, 2.0893089E-05, 2.2908816E-05, 2.5119019E-05, 2.7542459E-05, 3.0199708E-05, 3.3113323E-05, 3.6308040E-05, 3.9810973E-05, 4.3651868E-05, 4.7863323E-05, 5.2481097E-05, 5.7544377E-05, 6.3096166E-05, 6.9183567E-05, 7.5858276E-05, 8.3176950E-05, 9.1201720E-05, 1.0000071E-04, 1.0964860E-04, 1.2022730E-04, 1.3182664E-04, 1.4454505E-04, 1.5849050E-04, 1.7378137E-04, 1.9054749E-04, 2.0893120E-04, 2.2908850E-04, 2.5119056E-04, 2.7542500E-04, 3.0199753E-04, 3.3113372E-04, 3.6308094E-04, 3.9811034E-04, 4.3651930E-04, 4.7863391E-04, 5.2481168E-04, 5.7544466E-04, 6.3096255E-04, 6.9183676E-04, 7.5858383E-04, 8.3177071E-04, 9.1201853E-04, 1.0000085E-03, 1.0964876E-03, 1.2022748E-03, 1.3182682E-03, 1.4454524E-03, 1.5849071E-03, 1.7378164E-03, 1.9054777E-03, 2.0893149E-03, 2.2908885E-03, 2.5119095E-03, 2.7542540E-03, 3.0199795E-03, 3.3113416E-03, 3.6308144E-03, 3.9811088E-03, 4.3651992E-03, 4.7863466E-03, 5.2481247E-03, 5.7544550E-03, 6.3096345E-03, 6.9183763E-03, 7.5858496E-03, 8.3177192E-03, 9.1201989E-03, 1.0000098E-02, 1.0964892E-02, 1.2022764E-02, 1.3182701E-02, 1.4454544E-02, 1.5849093E-02, 1.7378187E-02, 1.9054806E-02, 2.0893177E-02, 2.2908917E-02, 2.5119130E-02, 2.7542580E-02, 3.0199837E-02, 3.3113468E-02, 3.6308199E-02, 3.9811146E-02, 4.3652054E-02, 4.7863536E-02, 5.2481323E-02, 5.7544626E-02, 6.3096434E-02, 6.9183864E-02, 7.5858615E-02, 8.3177313E-02, 9.1202110E-02, 0.1000011, 0.1096491, 0.1202278, 0.1318272, 0.1445457, 0.1584912, 0.1737821, 0.1905483, 0.2089321, 0.2290895, 0.2511916, 0.2754261, 0.3019988, 0.3311351, 0.3630825, 0.3981120, 0.4365212, 0.4786360, 0.5248140, 0.5754471, 0.6309653, 0.6918396, 0.7585871, 0.8317743, 0.9120225, 1.000013, 1.096492, 1.202280, 1.318274, 1.445459, 1.584914, 1.737824, 1.905486, 2.089324, 2.290898, 2.511920, 2.754266, 3.019992, 3.311356, 3.630830, 3.981126, 4.365218, 4.786367, 5.248147, 5.754479, 6.309661, 6.918406, 7.585882, 8.317756, 9.120237]
photon_flux_bin_min = [x*1000 for x in photon_flux_bin_min] # convert GeV to MeV

# This is the upper side of the energy bins for the photon flux simulated with FLUKA in 2025 at SwissFEL
photon_flux_bin_max = [1.0964782E-09, 1.2022645E-09, 1.3182568E-09, 1.4454400E-09, 1.5848935E-09, 1.7378012E-09, 1.9054613E-09, 2.0892970E-09, 2.2908686E-09, 2.5118878E-09, 2.7542302E-09, 3.0199536E-09, 3.3113132E-09, 3.6307830E-09, 3.9810746E-09, 4.3651625E-09, 4.7863051E-09, 5.2480797E-09, 5.7544050E-09, 6.3095800E-09, 6.9183175E-09, 7.5857844E-09, 8.3176479E-09, 9.1201207E-09, 1.0000014E-08, 1.0964798E-08, 1.2022662E-08, 1.3182588E-08, 1.4454421E-08, 1.5848958E-08, 1.7378039E-08, 1.9054641E-08, 2.0892999E-08, 2.2908720E-08, 2.5118911E-08, 2.7542342E-08, 3.0199580E-08, 3.3113182E-08, 3.6307885E-08, 3.9810804E-08, 4.3651681E-08, 4.7863118E-08, 5.2480868E-08, 5.7544135E-08, 6.3095889E-08, 6.9183272E-08, 7.5857955E-08, 8.3176602E-08, 9.1201329E-08, 1.0000028E-07, 1.0964812E-07, 1.2022679E-07, 1.3182606E-07, 1.4454442E-07, 1.5848980E-07, 1.7378063E-07, 1.9054669E-07, 2.0893029E-07, 2.2908752E-07, 2.5118950E-07, 2.7542382E-07, 3.0199621E-07, 3.3113230E-07, 3.6307938E-07, 3.9810863E-07, 4.3651744E-07, 4.7863188E-07, 5.2480942E-07, 5.7544219E-07, 6.3095985E-07, 6.9183363E-07, 7.5858065E-07, 8.3176718E-07, 9.1201463E-07, 1.0000042E-06, 1.0964828E-06, 1.2022696E-06, 1.3182624E-06, 1.4454462E-06, 1.5849004E-06, 1.7378088E-06, 1.9054694E-06, 2.0893056E-06, 2.2908785E-06, 2.5118984E-06, 2.7542419E-06, 3.0199662E-06, 3.3113279E-06, 3.6307990E-06, 3.9810920E-06, 4.3651808E-06, 4.7863259E-06, 5.2481018E-06, 5.7544294E-06, 6.3096072E-06, 6.9183475E-06, 7.5858170E-06, 8.3176838E-06, 9.1201591E-06, 1.0000056E-05, 1.0964844E-05, 1.2022713E-05, 1.3182643E-05, 1.4454482E-05, 1.5849026E-05, 1.7378110E-05, 1.9054720E-05, 2.0893089E-05, 2.2908816E-05, 2.5119019E-05, 2.7542459E-05, 3.0199708E-05, 3.3113323E-05, 3.6308040E-05, 3.9810973E-05, 4.3651868E-05, 4.7863323E-05, 5.2481097E-05, 5.7544377E-05, 6.3096166E-05, 6.9183567E-05, 7.5858276E-05, 8.3176950E-05, 9.1201720E-05, 1.0000071E-04, 1.0964860E-04, 1.2022730E-04, 1.3182664E-04, 1.4454505E-04, 1.5849050E-04, 1.7378137E-04, 1.9054749E-04, 2.0893120E-04, 2.2908850E-04, 2.5119056E-04, 2.7542500E-04, 3.0199753E-04, 3.3113372E-04, 3.6308094E-04, 3.9811034E-04, 4.3651930E-04, 4.7863391E-04, 5.2481168E-04, 5.7544466E-04, 6.3096255E-04, 6.9183676E-04, 7.5858383E-04, 8.3177071E-04, 9.1201853E-04, 1.0000085E-03, 1.0964876E-03, 1.2022748E-03, 1.3182682E-03, 1.4454524E-03, 1.5849071E-03, 1.7378164E-03, 1.9054777E-03, 2.0893149E-03, 2.2908885E-03, 2.5119095E-03, 2.7542540E-03, 3.0199795E-03, 3.3113416E-03, 3.6308144E-03, 3.9811088E-03, 4.3651992E-03, 4.7863466E-03, 5.2481247E-03, 5.7544550E-03, 6.3096345E-03, 6.9183763E-03, 7.5858496E-03, 8.3177192E-03, 9.1201989E-03, 1.0000098E-02, 1.0964892E-02, 1.2022764E-02, 1.3182701E-02, 1.4454544E-02, 1.5849093E-02, 1.7378187E-02, 1.9054806E-02, 2.0893177E-02, 2.2908917E-02, 2.5119130E-02, 2.7542580E-02, 3.0199837E-02, 3.3113468E-02, 3.6308199E-02, 3.9811146E-02, 4.3652054E-02, 4.7863536E-02, 5.2481323E-02, 5.7544626E-02, 6.3096434E-02, 6.9183864E-02, 7.5858615E-02, 8.3177313E-02, 9.1202110E-02, 0.1000011, 0.1096491, 0.1202278, 0.1318272, 0.1445457, 0.1584912, 0.1737821, 0.1905483, 0.2089321, 0.2290895, 0.2511916, 0.2754261, 0.3019988, 0.3311351, 0.3630825, 0.3981120, 0.4365212, 0.4786360, 0.5248140, 0.5754471, 0.6309653, 0.6918396, 0.7585871, 0.8317743, 0.9120225, 1.000013, 1.096492, 1.202280, 1.318274, 1.445459, 1.584914, 1.737824, 1.905486, 2.089324, 2.290898, 2.511920, 2.754266, 3.019992, 3.311356, 3.630830, 3.981126, 4.365218, 4.786367, 5.248147, 5.754479, 6.309661, 6.918406, 7.585882, 8.317756, 9.120237, 10.00014]
photon_flux_bin_max = [x*1000 for x in photon_flux_bin_max] # convert GeV to MeV

# This is the differential fluence of the photon (dN/dE) (Neutrons/MeVcm2) simulated with FLUKA in 2025
photon_fluence_differential = [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 8.3191216E-02, 0.1536413, 0.3709599, 0.6976327, 1.267720, 2.888060, 3.990444, 3.929904, 5.281829, 6.147330, 4.922317, 5.861687, 6.346646, 6.085726, 9.064732, 6.538879, 5.173975, 5.347501, 4.803934, 4.205269, 4.847298, 3.354748, 3.582505, 2.451476, 3.093173, 2.276625, 1.761723, 1.257364, 0.7813369, 1.292084, 0.6155038, 0.4682362, 0.4347267, 0.4119886, 0.3730924, 0.3099426, 0.2767032, 0.2499831, 0.2302541, 0.2511620, 0.1937544, 0.1821543, 0.1794374, 0.1589752, 0.1904185, 0.3911815, 9.0186112E-02, 8.3284244E-02, 7.4479416E-02, 7.5422302E-02, 0.1687552, 6.3414335E-02, 5.5944007E-02, 4.3859895E-02, 0.1247561, 3.2005467E-02, 3.0644124E-02, 4.3830752E-02, 2.1339100E-02, 4.6238333E-02, 8.6507993E-03, 4.1636656E-04, 4.4558244E-04, 1.9438034E-05, 1.6226371E-05, 1.1803066E-05, 9.0892654E-06, 6.1598885E-06, 4.7386902E-06, 3.3447382E-06, 1.9358627E-06, 2.3569362E-06, 1.0760388E-06, 7.9582520E-07, 6.0939391E-07, 5.7476495E-07, 1.5586380E-07, 1.4135684E-07, 6.7872328E-08, 5.0093163E-08, 1.5572498E-07, 9.4133959E-08, 7.4517743E-08, 5.2820617E-08, 6.2729349E-08, 2.0007262E-08, 2.7499635E-08, 2.7479903E-08, 1.4596507E-08, 2.3329338E-08, 1.4556578E-08, 9.9256354E-09, 8.1552551E-09, 4.2478039E-09, 6.5149059E-09, 2.4098767E-09, 1.6055445E-12, 0.000000, 0.000000, 1.7162482E-12, 1.5486168E-11, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000]

print("Entries for photon flux lower energy bin side :", len(photon_flux_bin_min))
print("Entries for photon flux upper energy bin side :", len(photon_flux_bin_max))
print("Entries for photon flux differential fluence :",  len(photon_fluence_differential))

# --- Plot the photon fluence (particles/cm2) and neutron differential fluence (particles/cm2MeV) ---

import matplotlib.pyplot as plt
import numpy as np

E_min = np.array(photon_flux_bin_min) # convert to numpy array
E_max = np.array(photon_flux_bin_max)
dN_dE = np.array(photon_fluence_differential)

dE = E_max - E_min # the width of each energy bin

fluence = dN_dE * dE # to get the fluence (neutrons/cm^2) I have to multiply my values for the bin width

E_center = np.sqrt(E_min * E_max) # the geometric mean for log-scaled bin centers

lethargy = dN_dE * (E_center/1000) # the lethargy 

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
plt.savefig('fluence_plot.png', dpi=300)

# --- Plot the fluence to H*(10) convertion function for photons (pSVcm2)
# --- and the FH40G (mounted on the WENDI-2) dose response function for photons (pSVcm2) ---

# Source Data 1: ICRP 74 Fluence-to-H*(10) for photons (ends at 10 MeV) ---
# Higher energies extension from Pelliccioni
energy_fluence_to_H10_photons = np.array([
    0.01, 0.015, 0.020, 0.030, 0.040, 0.050, 0.060, 0.080, 0.100, 0.150, 0.200, 0.300, 0.400, 0.500, 0.600, 0.800, 1, 1.5, 2, 3, 4, 5, 6, 8, 10,
    20.0, 30.0, 40.0, 50.0, 60.0, 80.0, 100.0
])

fluence_to_H10_photons = np.array([
    0.061, 0.83, 1.05, 0.81, 0.64, 0.55, 0.51, 0.53, 0.61, 0.89, 1.20, 1.80, 2.38, 2.93, 3.44, 4.38, 5.2, 6.9, 8.6, 11.1, 13.4, 15.5, 17.6, 21.6, 25.6,
    27.5, 30.4, 32.2, 33.6, 34.6, 35.8, 36.8
])

# Source Data 2: FH40G relative response for photons
# Data come from Thermo Scientific manual
energies_FH40G_response_keV = [26.62524823006097, 29.960345508968558, 34.09461133806839, 42.22588603606203, 50.36195117489987, 60.14381007118896, 66.88623229064154, 80.74587101741105, 85.13420252521837, 97.73917544482781, 105.17388736956066, 121.42424146875841, 143.9705154217793, 168.4071179205905, 199.52553897891215, 216.31140936534436, 255.3865729049049, 317.3167002307814, 387.12473233690235, 471.1968982635771, 571.0906460179347, 689.038993652611, 839.1248381495312, 1008.7087971337812, 1250.4299345029056, 1383.7752932440596, 1696.258688898452, 2078.2030257643482, 2563.486050547929, 3143.5071471413735, 3840.0572543475287, 4497.044442869985, 5244.8650410399105, 5719.7111616050715, 6129.629736882611]
energy_FH40G_response = [x/1000 for x in energies_FH40G_response_keV] # keV to MeV convertion

FH40G_relative_response = [0.734272038627258, 0.8376929729708648, 0.9013583308063499, 0.9248843356601082, 0.9205024975697081, 0.8882915999169264, 0.8890219062653264, 0.9140529857244122, 0.9447262423739539, 1.0345079012516611, 1.0673808523230859, 1.0607486176344119, 0.9885044515535829, 0.9152951890459897, 0.8545951284958906, 0.827573403588349, 0.8161459130633182, 0.8504338448727912, 0.8858329343787081, 0.930001745324918, 0.9691485056996071, 1.0026140872096934, 1.0518100189450632, 1.0928637661771632, 1.127260317649135, 1.1437246793818625, 1.1624133065911855, 1.165373728667303, 1.1744667739862733, 1.1907339822561882, 1.2187211936072355, 1.2644469513853882, 1.3517445936366819, 1.4560596413601052, 1.567704078697578]

# --- 2. PLOT 1: RAW FLUENCE-TO-H*(10) CONVERSION FUNCTION ---

fig1, ax1 = plt.subplots(figsize=(8, 5))
ax1.loglog(energy_fluence_to_H10_photons, fluence_to_H10_photons, 
           color='blue', marker='o', linestyle='-', linewidth=1.5, label='ICRP 74 + Pelliccioni')
ax1.set_xlabel('Energy (MeV)', fontsize=11)
ax1.set_ylabel('Fluence-to-$H^*(10)$ Conversion Factor ($pSv \cdot cm^2$)', fontsize=11)
ax1.set_title('Raw Photon Fluence-to-$H^*(10)$ Conversion Coefficients', fontsize=12, pad=10)
ax1.grid(True, which="both", linestyle="--", alpha=0.5)
ax1.legend()
plt.tight_layout()
plt.savefig('photon_h10_conversion_raw.png', dpi=300)
plt.close(fig1)

# --- 3. PLOT 2: RAW FH40G RELATIVE RESPONSE FUNCTION ---

fig2, ax2 = plt.subplots(figsize=(8, 5))
# Semilogx is preferred because relative response is close to 1.0
ax2.semilogx(energy_FH40G_response, FH40G_relative_response, 
             color='purple', marker='s', linestyle='-', linewidth=1.5, label='FH40G (Thermo Scientific)')
ax2.axhline(1.0, color='red', linestyle='--', alpha=0.7, label='Ideal Response (1.0)')
ax2.set_xlabel('Energy (MeV)', fontsize=11)
ax2.set_ylabel('Relative Response (Measured / Ideal)', fontsize=11)
ax2.set_title('Raw FH40G Energy Dependence of Relative Response', fontsize=12, pad=10)
ax2.grid(True, which="both", linestyle="--", alpha=0.5)
ax2.legend()
plt.tight_layout()
plt.savefig('fh40g_relative_response_raw.png', dpi=300)
plt.close(fig2)

# --- 4. PLOT 3: OVERLAID ABSOLUTE DOSE RESPONSES ---

from scipy.interpolate import interp1d
# To compute the absolute response function, we need the relative response on the ICRP energy grid.
# We perform log-log interpolation of the FH40G response onto energy_fluence_to_H10_photons.
log10_E_target = np.log10(energy_fluence_to_H10_photons)
log10_E_source = np.log10(energy_FH40G_response)
log10_R_source = np.log10(FH40G_relative_response)

# Interpolating using scipy's linear interpolator in log-space (extrapolating where necessary)
interp_func = interp1d(log10_E_source, log10_R_source, kind='linear', fill_value='extrapolate')
log10_R_interpolated = interp_func(log10_E_target)
FH40G_relative_response_interp = 10**log10_R_interpolated

# Absolute response function: h10_ideal [pSv*cm^2] * relative_response [dimensionless]
FH40G_absolute_response_to_H10 = FH40G_relative_response_interp * fluence_to_H10_photons

# Plotting the overlaid ideal vs measured absolute responses
fig3, ax3 = plt.subplots(figsize=(8, 5))
ax3.loglog(energy_fluence_to_H10_photons, fluence_to_H10_photons, 
           color='blue', marker='o', linestyle='-', linewidth=1.8, label='Ideal $H^*(10)$ Conversion')
ax3.loglog(energy_fluence_to_H10_photons, FH40G_absolute_response_to_H10, 
           color='orange', marker='^', linestyle='--', linewidth=1.8, label='FH40G Absolute Photon Response')

ax3.set_xlabel('Energy (MeV)', fontsize=11)
ax3.set_ylabel('Response Factor ($pSv \cdot cm^2$)', fontsize=11)
ax3.set_title('Comparison of Ideal and FH40G Absolute Photon Dose Response', fontsize=12, pad=10)
ax3.grid(True, which="both", linestyle="--", alpha=0.5)
ax3.legend()
plt.tight_layout()
plt.savefig('fh40g_vs_h10_absolute_response.png', dpi=300)
plt.close(fig3)

# Create a figure with 2 rows, 1 column, sharing the X-axis
# The height ratio gives more room for the fluence plot (top)
fig_stacked, (ax_top, ax_bottom) = plt.subplots(
    2, 1,
    figsize=(9, 8),
    sharex=True,
    gridspec_kw={'height_ratios': [2.5, 1]}
)

# Top Subplot: Simulated Photon Fluence from FLUKA (log-log scale)
ax_top.plot(E_center, fluence, color='blue', label='Photon Fluence', linestyle='-', marker='.')
ax_top.set_yscale('log')
ax_top.set_xscale('log') # Ensure target X-axis of top plot matches log coordinates
ax_top.set_ylabel('Fluence (particles/$cm^2$)', fontsize=12)
ax_top.set_title('Simulated Photon Spectrum (SwissFEL) & Raw FH40G Response', fontsize=14, pad=15)
ax_top.grid(True, which="both", ls="--", alpha=0.5)
ax_top.legend(loc='upper right')

# Hide X-axis tick labels for the top subplot to avoid labels overlapping with the bottom subplot
ax_top.tick_params(axis='x', labelbottom=False)

# Bottom Subplot: Raw, uninterpolated FH40G relative response
# We use standard plot coordinates but on log X-axis (shared) to keep coordinates matched
ax_bottom.plot(energy_FH40G_response, FH40G_relative_response, color='purple', marker='s', linestyle='-', label='Raw FH40G response')
ax_bottom.axhline(1.0, color='red', linestyle='--', alpha=0.8, label='Ideal (Ratio = 1.0)')

ax_bottom.set_xscale('log') # Synchronizes and scales the shared X axis automatically
ax_bottom.set_xlabel('Energy ($MeV$)', fontsize=12)
ax_bottom.set_ylabel('Relative Response', fontsize=12)
ax_bottom.grid(True, which="both", ls="--", alpha=0.5)
ax_bottom.legend(loc='lower left')

# Adjust layout to eliminate whitespace and stick pads together
plt.subplots_adjust(hspace=0.05)

# Save the newly requested stacked plot independently
plt.savefig('stacked_fluence_and_raw_relative_response.png', dpi=300, bbox_inches='tight')
plt.close(fig_stacked)

# --- GLOBAL BIAS CALCULATION (FH40G Over/Under-response for SwissFEL Photon Spectrum) ---

# 0. Filter out bins with zero energy or zero fluence.
# This prevents "RuntimeWarning: divide by zero encountered in log10" which causes interpolation to fail.
valid_indices = (E_center > 0) & (fluence > 0)
E_center_valid = E_center[valid_indices]
fluence_valid = fluence[valid_indices]

# 1. We must interpolate the FH40G relative response onto the simulated photon energy grid.
# The source x array is energy_FH40G_response, and the y array is FH40G_relative_response.
log_FH40G_relative_response = np.log10(FH40G_relative_response)
f_interp_ratio_log = interp1d(
    np.log10(energy_FH40G_response),
    log_FH40G_relative_response,
    kind='linear',
    bounds_error=False,
    fill_value="extrapolate" # Allows calculation even if spectrum exceeds FH40G limits
)

# Evaluate the interpolation function at our VALID simulated energy bins
ratio_interp = 10**(f_interp_ratio_log(np.log10(E_center_valid)))

# 2. We must do the exact same log-log interpolation for the ICRP H*(10) conversion factors.
# We map fluence_to_H10_photons onto our E_center_valid grid.
f_interp_h10_log = interp1d(
    np.log10(energy_fluence_to_H10_photons),
    np.log10(fluence_to_H10_photons),
    kind='linear',
    bounds_error=False,
    fill_value="extrapolate"
)

h10_interp = 10**(f_interp_h10_log(np.log10(E_center_valid)))

# 3. FOLDING: Calculate the dose for each energy bin
# 'fluence_valid' is already integrated per bin (dN_dE * dE) so its unit is [photons / cm^2]
# 'h10_interp' unit is [pSv * cm^2]
# The product directly yields the absolute dose [pSv] per bin.

# The "True" expected environmental dose
ideal_dose_spectrum = fluence_valid * h10_interp

# The Dose that the FH40G would actually register, skewed by its response ratio
measured_dose_spectrum = fluence_valid * h10_interp * ratio_interp

# 4. Integrate (sum) over the entire spectrum
# We use np.nansum to safely ignore any potential NaN values from extreme extrapolations
total_ideal_dose = np.nansum(ideal_dose_spectrum)
total_measured_dose = np.nansum(measured_dose_spectrum)

# 5. Calculate the global correction factor for this specific environment
global_bias = total_measured_dose / total_ideal_dose

print("\n--- DOSIMETRY RESULTS ---")
print(f"Total Ideal Expected Dose: {total_ideal_dose:.3e} pSv")
print(f"Total FH40G Measured Dose: {total_measured_dose:.3e} pSv")
print(f"Global Correction Factor (Bias): {global_bias:.3f}")

if global_bias < 1.0:
    print(f"-> The FH40G UNDER-RESPONDS by {(1.0 - global_bias)*100:.1f}%.")
    print(f"-> Field measurements must be multiplied by {1.0/global_bias:.3f} to find the true H*(10).")
else:
    print(f"-> The FH40G OVER-RESPONDS by {(global_bias - 1.0)*100:.1f}%.")
    print(f"-> Field measurements must be divided by {global_bias:.3f} to find the true H*(10).")
