'''
This code was created to calculate the correction of the WENDI-2 neutron detector dose measurement when used in the SwissFel neutron radiation environment.
Specifically the neutron fluence was calculated with FLUKA based on the 2025 measurement campaign at the PSI SwissFel.
Data for the WENDI-2 neutron response come from literature reported below in comments.
'''

# This is the lower side of the energy bins for the neutron flux simulated with FLUKA in 2025 at SwissFEL
neutron_flux_bin_min =  [1.0000000E-12, 1.1271975E-12, 1.2705742E-12, 1.4321880E-12, 1.6143588E-12, 1.8197013E-12, 2.0511626E-12, 2.3120653E-12, 2.6061542E-12, 2.9376503E-12, 3.3113124E-12, 3.7325030E-12, 4.2072678E-12, 4.7424222E-12, 5.3456462E-12, 6.0255989E-12, 6.7920400E-12, 7.6559705E-12, 8.6297905E-12, 9.7274784E-12, 1.0964789E-11, 1.2359482E-11, 1.3931579E-11, 1.5703640E-11, 1.7701103E-11, 1.9952638E-11, 2.2490567E-11, 2.5351308E-11, 2.8575930E-11, 3.2210720E-11, 3.6307842E-11, 4.0926110E-11, 4.6131807E-11, 5.1999658E-11, 5.8613885E-11, 6.6069421E-11, 7.4473282E-11, 8.3946100E-11, 9.4623837E-11, 1.0665975E-10, 1.2022661E-10, 1.3551912E-10, 1.5275682E-10, 1.7218710E-10, 1.9408886E-10, 2.1877648E-10, 2.4660432E-10, 2.7797176E-10, 3.1332906E-10, 3.5318373E-10, 3.9810782E-10, 4.4874612E-10, 5.0582555E-10, 5.7016530E-10, 6.4268890E-10, 7.2443723E-10, 8.1658386E-10, 9.2045122E-10, 1.0375304E-09, 1.1695016E-09, 1.3182593E-09, 1.4859387E-09, 1.6749463E-09, 1.8879953E-09, 2.1281434E-09, 2.3988380E-09, 2.7039644E-09, 3.0479019E-09, 3.4355871E-09, 3.8725854E-09, 4.3651691E-09, 4.9204072E-09, 5.5462706E-09, 6.2517418E-09, 7.0469484E-09, 7.9433020E-09, 8.9536698E-09, 1.0092554E-08, 1.1376303E-08, 1.2823340E-08, 1.4454436E-08, 1.6293004E-08, 1.8365434E-08, 2.0701469E-08, 2.3334646E-08, 2.6302754E-08, 2.9648398E-08, 3.3419603E-08, 3.7670489E-08, 4.2462077E-08, 4.7863153E-08, 5.3951222E-08, 6.0813683E-08, 6.8549042E-08, 7.7268297E-08, 8.7096630E-08, 9.8175100E-08, 1.1066273E-07, 1.2473876E-07, 1.4060521E-07, 1.5848983E-07, 1.7864934E-07, 2.0137311E-07, 2.2698727E-07, 2.5585948E-07, 2.8840412E-07, 3.2508845E-07, 3.6643888E-07, 4.1304892E-07, 4.6558779E-07, 5.2480937E-07, 5.9156383E-07, 6.6680923E-07, 7.5162569E-07, 8.4723058E-07, 9.5499615E-07, 1.0764694E-06, 1.2133936E-06, 1.3677343E-06, 1.5417065E-06, 1.7378076E-06, 1.9588524E-06, 2.2080135E-06, 2.4888673E-06, 2.8054451E-06, 3.1622910E-06, 3.5645262E-06, 4.0179252E-06, 4.5289949E-06, 5.1050720E-06, 5.7544244E-06, 6.4863725E-06, 7.3114229E-06, 8.2414172E-06, 9.2897062E-06, 1.0471332E-05, 1.1803259E-05, 1.3304604E-05, 1.4996917E-05, 1.6904489E-05, 1.9054694E-05, 2.1478407E-05, 2.4210405E-05, 2.7289909E-05, 3.0761115E-05, 3.4673852E-05, 3.9084276E-05, 4.4055701E-05, 4.9659477E-05, 5.5976037E-05, 6.3096049E-05, 7.1121707E-05, 8.0168211E-05, 9.0365400E-05, 1.0185967E-04, 1.1481595E-04, 1.2942024E-04, 1.4588219E-04, 1.6443802E-04, 1.8535415E-04, 2.0893072E-04, 2.3550619E-04, 2.6546197E-04, 2.9922806E-04, 3.3728912E-04, 3.8019146E-04, 4.2855091E-04, 4.8306148E-04, 5.4450566E-04, 6.1376544E-04, 6.9183490E-04, 7.7983458E-04, 8.7902747E-04, 9.9083758E-04, 1.1168697E-03, 1.2589328E-03, 1.4190659E-03, 1.5995674E-03, 1.8030284E-03, 2.0323689E-03, 2.2908812E-03, 2.5822758E-03, 2.9107349E-03, 3.2809728E-03, 3.6983043E-03, 4.1687191E-03, 4.6989699E-03, 5.2966666E-03, 5.9703896E-03, 6.7298091E-03, 7.5858231E-03, 8.5507212E-03, 9.6383514E-03, 1.0864326E-02, 1.2246241E-02, 1.3803933E-02, 1.5559757E-02, 1.7538920E-02, 1.9769827E-02, 2.2284498E-02, 2.5119031E-02, 2.8314108E-02, 3.1915594E-02, 3.5975177E-02, 4.0551126E-02, 4.5709126E-02, 5.1523220E-02, 5.8076844E-02, 6.5464064E-02, 7.3790938E-02, 8.3176956E-02, 9.3756847E-02, 0.1056825, 0.1191250, 0.1342774, 0.1513572, 0.1706095, 0.1923105, 0.2167720, 0.2443448, 0.2754248, 0.3104582, 0.3499477, 0.3944602, 0.4446345, 0.5011910, 0.5649412, 0.6368003, 0.7177996, 0.8091020, 0.9120178, 1.028024, 1.158786, 1.306181, 1.472324, 1.659600, 1.870697, 2.108645, 2.376859, 2.679189, 3.019976, 3.404109, 3.837103, 4.325173, 4.875324, 5.495454, 6.194462, 6.982381, 7.870522, 8.871633]
neutron_flux_bin_min = [x*1000 for x in neutron_flux_bin_min] # convert GeV to MeV

# This is the upper side of the energy bins for the neutron flux simulated with FLUKA in 2025 at SwissFEL
neutron_flux_bin_max = [1.1271975E-12, 1.2705742E-12, 1.4321880E-12, 1.6143588E-12, 1.8197013E-12, 2.0511626E-12, 2.3120653E-12, 2.6061542E-12, 2.9376503E-12, 3.3113124E-12, 3.7325030E-12, 4.2072678E-12, 4.7424222E-12, 5.3456462E-12, 6.0255989E-12, 6.7920400E-12, 7.6559705E-12, 8.6297905E-12, 9.7274784E-12, 1.0964789E-11, 1.2359482E-11, 1.3931579E-11, 1.5703640E-11, 1.7701103E-11, 1.9952638E-11, 2.2490567E-11, 2.5351308E-11, 2.8575930E-11, 3.2210720E-11, 3.6307842E-11, 4.0926110E-11, 4.6131807E-11, 5.1999658E-11, 5.8613885E-11, 6.6069421E-11, 7.4473282E-11, 8.3946100E-11, 9.4623837E-11, 1.0665975E-10, 1.2022661E-10, 1.3551912E-10, 1.5275682E-10, 1.7218710E-10, 1.9408886E-10, 2.1877648E-10, 2.4660432E-10, 2.7797176E-10, 3.1332906E-10, 3.5318373E-10, 3.9810782E-10, 4.4874612E-10, 5.0582555E-10, 5.7016530E-10, 6.4268890E-10, 7.2443723E-10, 8.1658386E-10, 9.2045122E-10, 1.0375304E-09, 1.1695016E-09, 1.3182593E-09, 1.4859387E-09, 1.6749463E-09, 1.8879953E-09, 2.1281434E-09, 2.3988380E-09, 2.7039644E-09, 3.0479019E-09, 3.4355871E-09, 3.8725854E-09, 4.3651691E-09, 4.9204072E-09, 5.5462706E-09, 6.2517418E-09, 7.0469484E-09, 7.9433020E-09, 8.9536698E-09, 1.0092554E-08, 1.1376303E-08, 1.2823340E-08, 1.4454436E-08, 1.6293004E-08, 1.8365434E-08, 2.0701469E-08, 2.3334646E-08, 2.6302754E-08, 2.9648398E-08, 3.3419603E-08, 3.7670489E-08, 4.2462077E-08, 4.7863153E-08, 5.3951222E-08, 6.0813683E-08, 6.8549042E-08, 7.7268297E-08, 8.7096630E-08, 9.8175100E-08, 1.1066273E-07, 1.2473876E-07, 1.4060521E-07, 1.5848983E-07, 1.7864934E-07, 2.0137311E-07, 2.2698727E-07, 2.5585948E-07, 2.8840412E-07, 3.2508845E-07, 3.6643888E-07, 4.1304892E-07, 4.6558779E-07, 5.2480937E-07, 5.9156383E-07, 6.6680923E-07, 7.5162569E-07, 8.4723058E-07, 9.5499615E-07, 1.0764694E-06, 1.2133936E-06, 1.3677343E-06, 1.5417065E-06, 1.7378076E-06, 1.9588524E-06, 2.2080135E-06, 2.4888673E-06, 2.8054451E-06, 3.1622910E-06, 3.5645262E-06, 4.0179252E-06, 4.5289949E-06, 5.1050720E-06, 5.7544244E-06, 6.4863725E-06, 7.3114229E-06, 8.2414172E-06, 9.2897062E-06, 1.0471332E-05, 1.1803259E-05, 1.3304604E-05, 1.4996917E-05, 1.6904489E-05, 1.9054694E-05, 2.1478407E-05, 2.4210405E-05, 2.7289909E-05, 3.0761115E-05, 3.4673852E-05, 3.9084276E-05, 4.4055701E-05, 4.9659477E-05, 5.5976037E-05, 6.3096049E-05, 7.1121707E-05, 8.0168211E-05, 9.0365400E-05, 1.0185967E-04, 1.1481595E-04, 1.2942024E-04, 1.4588219E-04, 1.6443802E-04, 1.8535415E-04, 2.0893072E-04, 2.3550619E-04, 2.6546197E-04, 2.9922806E-04, 3.3728912E-04, 3.8019146E-04, 4.2855091E-04, 4.8306148E-04, 5.4450566E-04, 6.1376544E-04, 6.9183490E-04, 7.7983458E-04, 8.7902747E-04, 9.9083758E-04, 1.1168697E-03, 1.2589328E-03, 1.4190659E-03, 1.5995674E-03, 1.8030284E-03, 2.0323689E-03, 2.2908812E-03, 2.5822758E-03, 2.9107349E-03, 3.2809728E-03, 3.6983043E-03, 4.1687191E-03, 4.6989699E-03, 5.2966666E-03, 5.9703896E-03, 6.7298091E-03, 7.5858231E-03, 8.5507212E-03, 9.6383514E-03, 1.0864326E-02, 1.2246241E-02, 1.3803933E-02, 1.5559757E-02, 1.7538920E-02, 1.9769827E-02, 2.2284498E-02, 2.5119031E-02, 2.8314108E-02, 3.1915594E-02, 3.5975177E-02, 4.0551126E-02, 4.5709126E-02, 5.1523220E-02, 5.8076844E-02, 6.5464064E-02, 7.3790938E-02, 8.3176956E-02, 9.3756847E-02, 0.1056825, 0.1191250, 0.1342774, 0.1513572, 0.1706095, 0.1923105, 0.2167720, 0.2443448, 0.2754248, 0.3104582, 0.3499477, 0.3944602, 0.4446345, 0.5011910, 0.5649412, 0.6368003, 0.7177996, 0.8091020, 0.9120178, 1.028024, 1.158786, 1.306181, 1.472324, 1.659600, 1.870697, 2.108645, 2.376859, 2.679189, 3.019976, 3.404109, 3.837103, 4.325173, 4.875324, 5.495454, 6.194462, 6.982381, 7.870522, 8.871633, 10.00008]
neutron_flux_bin_max = [x*1000 for x in neutron_flux_bin_max] # convert GeV to MeV

# This is the differential fluence of the neutrons (dN/dE) (Neutrons/MeVcm2) simulated with FLUKA in 2025
neutron_fluence_differential = [257441.1, 283464.5, 119988.8, 576473.2, 196380.1, 339733.3, 677608.9, 636745.8, 431372.0, 725778.5, 796823.7, 971698.1, 1144935., 1510168., 1587017., 2000684., 1646242., 1758530., 2217067., 2427907., 2509081., 2663888., 3187773., 3522366., 3915851., 3884326., 4111081., 4379386., 4422306., 4475590., 4473106., 4280388., 4000730., 3650752., 3175299., 2643124., 2136643., 1740802., 1286592., 938048.9, 567868.2, 384582.4, 240247.3, 139243.4, 98878.06, 51426.49, 31561.51, 20934.41, 17384.44, 12505.40, 11315.13, 11407.50, 11303.16, 9860.485, 7513.986, 6732.945, 5987.369, 4923.546, 5571.510, 3368.001, 2628.181, 3105.958, 3326.066, 2514.458, 2015.692, 1863.885, 1523.825, 1839.298, 1267.291, 836.0508, 1019.351, 820.3976, 732.7415, 646.1347, 593.5504, 438.0917, 518.4284, 385.8990, 269.9217, 284.1479, 289.4415, 231.5765, 245.1959, 162.3932, 143.4353, 135.3934, 121.6911, 115.4552, 70.71508, 75.30845, 67.37531, 74.66490, 69.40839, 38.70984, 37.59397, 40.05275, 36.71345, 28.54985, 19.70844, 21.52743, 19.95745, 17.28657, 17.94884, 15.02095, 15.47954, 8.132508, 8.765331, 8.018218, 8.206712, 5.382307, 4.791873, 5.204505, 4.814923, 3.595470, 4.028876, 3.693014, 3.731691, 2.489256, 2.668991, 1.932511, 1.957079, 1.494171, 1.348751, 1.338707, 0.9125900, 1.063494, 0.9211050, 0.7348630, 0.7605793, 0.5072417, 0.5435232, 0.5594368, 0.4309097, 0.3656132, 0.3011673, 0.2737519, 0.2626331, 0.2453497, 0.1974537, 0.2156077, 0.1644257, 0.1989160, 0.2019996, 9.2423871E-02, 0.1314488, 9.4106168E-02, 0.1086253, 8.7195858E-02, 8.7628901E-02, 9.8621875E-02, 7.8335986E-02, 5.5818714E-02, 4.9635205E-02, 4.6083380E-02, 5.6160398E-02, 5.0352409E-02, 4.7821388E-02, 4.5129653E-02, 3.9930511E-02, 3.0939113E-02, 3.6909305E-02, 3.3100907E-02, 3.3176709E-02, 3.4289464E-02, 3.0670675E-02, 1.8646779E-02, 1.7606765E-02, 2.3456389E-02, 2.3514044E-02, 1.8386025E-02, 1.9189307E-02, 1.6932106E-02, 1.0463245E-02, 1.0179237E-02, 8.4376968E-03, 6.5458086E-03, 5.7246075E-03, 4.5863995E-03, 3.6422554E-03, 3.5197935E-03, 3.3297974E-03, 2.3942853E-03, 1.5635507E-03, 9.7079924E-04, 8.9010940E-04, 6.6569954E-04, 5.3365791E-04, 4.4401825E-04, 4.5168030E-04, 2.6840030E-04, 2.0608885E-04, 1.5773707E-04, 1.2821931E-04, 1.1463290E-04, 1.0167091E-04, 8.2477207E-05, 9.6304022E-05, 7.2679344E-05, 7.9365789E-05, 7.1202208E-05, 7.3364419E-05, 6.6645072E-05, 6.7403933E-05, 6.6712448E-05, 6.9035341E-05, 7.0311653E-05, 6.7523652E-05, 6.5300708E-05, 5.9146256E-05, 4.7710659E-05, 4.1036394E-05, 3.4785320E-05, 2.7192322E-05, 2.1091395E-05, 1.4831823E-05, 9.3695271E-06, 6.1699766E-06, 3.2672858E-06, 1.9194533E-06, 7.0922079E-07, 2.8315185E-07, 5.1303598E-08, 2.9197555E-08, 3.8648871E-09, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000]

print("Entries for neutron flux lower energggy bin side :", len(neutron_flux_bin_min))
print("Entries for neutron flux upper energy bin side :", len(neutron_flux_bin_max))
print("Entries for neutron flux differential fluence :",  len(neutron_fluence_differential))

# --- Plot the neutron fluence (particles/cm2) and neutron differential fluence (particles/cm2MeV) ---

import matplotlib.pyplot as plt
import numpy as np

E_min = np.array(neutron_flux_bin_min) # convert to numpy array
E_max = np.array(neutron_flux_bin_max)
dN_dE = np.array(neutron_fluence_differential)

dE = E_max - E_min # the width of each energy bin

fluence = dN_dE * dE # to get the fluence (neutrons/cm^2) I have to multiply my values for the bin width

E_center = np.sqrt(E_min * E_max) # the geometric mean for log-scaled bin centers

# Calculate the lethargy fluence (E * dN/dE)
# Since dN_dE is in MeV^-1 cm^-2 and E_center is in MeV, multiply directly by E_center
lethargy = dN_dE * E_center

fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot Neutron Fluence on the primary Y-axis (left)
color1 = 'blue'
ax1.plot(E_center, fluence, label='Neutron Fluence', color=color1, marker='.', linestyle='-')
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

plt.title('Neutron Fluence and Lethargy vs Energy (2025)', fontsize=13, pad=10)
plt.tight_layout()
plt.savefig('fluence_plot.png', dpi=300)

# --- Plot the fluence to H*(10) convertion function for neutrons (pSVcm2)
# --- and the WENDI-2 dose response function for neutrons (pSVcm2) ---

# This is the fluence to H*(10) convertion function in pSVcm2, energy bins in MeV
# Numbers are taken from "MCNPX SIMULATIONS OF THE RESPONSE OF THE EXTENDED-RANGE REM METER WENDI-2", DOI:10.2298/NTRP140SS25S
energy_fluence_to_H10_function = [9.492218410280988e-9, 7.79370003310337e-8, 1.8450523636359488e-7, 6.391572541760222e-7, 0.000001196590178695872, 0.0000027823102149957592, 0.000005307285683717842, 0.000010231106652003436, 0.000023278138167773893, 0.000042483917203395035, 0.00008076191527801742, 0.00018928383651851429, 0.0003635068849352923, 0.0006903189177272841, 0.0015915557824633265, 0.002983585657778197, 0.005645429347979109, 0.012824224181601233, 0.02477975812960878, 0.04713481248081918, 0.06763915344644195, 0.11162795508530567, 0.14910430495168958, 0.2021168295695759, 0.2825530174737817, 0.3761227679543664, 0.5621630080012422, 0.8581092921177734, 1.193311490116029, 1.9315797200635523, 3.0635427165248004, 5.924792950263549, 10.620032233831877, 15.879348937441032, 25.5432651555736, 37.24580147079381, 60.24223934384477, 92.0448653985943, 117.69899660418108, 169.5378901352275, 315.4687877287317, 401.7072772240769, 484.8280013467348, 592.2872514265484, 775.1935095763772, 938.3016521377199, 1371.130530716348, 1805.7079793741932, 2623.723141019056, 4015.405527485102]

fluence_to_H10_function = [6.466250424686161, 8.799679730059975, 10.311071254352676, 12.550073554335057, 13.110995769306358, 13.04732071640402, 12.938089587841061, 12.36783915759269, 11.533934092774762, 10.919057066048893, 10.306481384258957, 9.570783817289552, 9.149872743451809, 8.556373881792219, 8.014033284880584, 7.680080716074246, 7.548324338039095, 7.711408181310479, 10.092721735729185, 15.751225781458523, 22.92952436337824, 39.43955380203264, 58.34955046204815, 85.68835482460437, 129.1868168874242, 168.6254770987624, 231.96883530095405, 318.4074658501491, 370.05932308196606, 419.7154323430968, 416.52189589866686, 404.15489820942605, 400.77134563145006, 470.27585035359493, 592.2088584676992, 515.0339239286063, 405.1138282879553, 319.4097514591874, 283.28833951915, 242.9008838853542, 303.56107190068565, 343.66199531090075, 413.0752985273366, 478.6141706126125, 562.9223957316359, 651.3011760820857, 723.0153836888301, 790.8497596100315, 854.9824782620643, 935.9175337863275]

# This is the WENDI-2 dose response function in pSVcm2, energy bins in MeV
# Numbers are taken from "MCNPX SIMULATIONS OF THE RESPONSE OF THE EXTENDED-RANGE REM METER WENDI-2", 10.2298/NTRP140SS25S
energies_WENDI2_doseresponse_function = [9.137925994590346e-9, 7.822043113804741e-8, 1.8154295293328923e-7, 6.349202085180043e-7, 0.000001267741853305143, 0.000002819237952669704, 0.000005453590270673759, 0.000009896044991279358, 0.000023116663034636025, 0.00004326347316693977, 0.00008279645944228825, 0.0001883405382948626, 0.00036460471858307437, 0.0006874936771417217, 0.0015746535267530247, 0.0029627979950382897, 0.0057797082297750685, 0.013766213600880917, 0.024397095032918415, 0.047110528823223634, 0.06552395162534924, 0.10869962793059527, 0.14815026334713555, 0.30197775027435114, 0.3993755052185611, 0.5988765149606193, 0.9254557509725517, 1.2163161915751277, 2.0140300572093306, 3.092001818908333, 6.157957485276503, 9.11940736024237, 12.002671917705928, 18.578966817595532, 27.65666167054522, 65.4082843806726, 141.83993967991216, 207.37936888861014, 320.7192736048112, 406.66220030437904, 604.7663239231711, 931.8331044860364, 1462.3012432855219, 1854.164585765732, 2699.249805199586, 4372.848974477643]

WENDI2_doseresponse_function = [3.1079997309778444, 4.277584357993236, 5.378853528102297, 8.863597258286406, 11.516159203730442, 15.471208546638781, 17.55858062145924, 20.147627889989057, 23.97033040853062, 26.692419091785187, 28.436131758403, 31.430090804570384, 34.65750058074926, 36.95090808067225, 41.10017849260949, 44.70133830473867, 48.12517382742031, 53.52941911359774, 58.09280042117876, 64.65782778068517, 69.12268144379307, 78.58149103614029, 85.50740728979144, 117.57523302936686, 137.51604066368571, 171.5396603430618, 232.71876087002315, 283.69553149892187, 347.26856880825335, 385.51288410311565, 358.2476521556585, 325.24780893336924, 287.6265077647707, 273.7220102151355, 279.36761290821244, 286.3718208340026, 343.15831969506036, 399.8514284135687, 478.2849604994173, 554.9864296673361, 748.5904606577901, 981.6656194544113, 1220.621175847281, 1354.1794838429043, 1636.6220670095445, 1947.2816345231436]

# Explicitly create a brand new, clean figure canvas to avoid overlays
fig, ax = plt.subplots(figsize=(8, 6))
# Plotting both curves on the new axes using a log-log scale
ax.loglog(energy_fluence_to_H10_function, fluence_to_H10_function, label='Fluence to $H^*(10)$ Conversion', color='blue')
ax.loglog(energies_WENDI2_doseresponse_function, WENDI2_doseresponse_function, label='WENDI-2 Dose Response', color='orange')
# Adding labels, title and grid to the specific axes
ax.set_xlabel('Energy ($MeV$)')
ax.set_ylabel('Conversion Factor ($pSv cm^2$)')
ax.set_title('Fluence-to-$H^*(10)$ Conversion Function and WENDI-2 Dose Response Function')
ax.grid(True, which="both", ls="--", alpha=0.5)
ax.legend()
# Save the new figure independently
plt.tight_layout()
plt.savefig('wendi2_vs_h10_comparison.png', dpi=300)
# Optional: Close the figure to free up memory
plt.close(fig)

# We create now the ratio plot between the WENDI2 dose response function and the H*(10) convertion function
import numpy as np

# Convert lists to numpy arrays for mathematical operations
x_h10 = np.array(energy_fluence_to_H10_function)
y_h10 = np.array(fluence_to_H10_function)

x_wendi = np.array(energies_WENDI2_doseresponse_function)
y_wendi = np.array(WENDI2_doseresponse_function)

# Perform interpolation in log-log space due to data spanning multiple decades
log_x_h10 = np.log10(x_h10)
log_y_h10 = np.log10(y_h10)
log_x_wendi = np.log10(x_wendi)

# Interpolate H*(10) values onto the WENDI-2 energy grid
log_y_h10_interp = np.interp(log_x_wendi, log_x_h10, log_y_h10)
y_h10_interp = 10**log_y_h10_interp

# Calculate the ratio (WENDI-2 Response / H*(10) Conversion)
ratio = y_wendi / y_h10_interp

# Create a brand new figure for the ratio plot
fig, ax = plt.subplots(figsize=(8, 5))

# Plot the ratio (using semilogx since the ratio itself is close to O(1))
ax.loglog(x_wendi, ratio, color='purple', label='WENDI-2 / $H^*(10)$', lw=2)

# Add a horizontal baseline at 1.0 to easily evaluate over/under-response
ax.axhline(1.0, color='red', linestyle='--', alpha=0.7, label='Ideal Response (1.0)')

# Formatting the plot
ax.set_xlabel('Energy ($MeV$)')
ax.set_ylabel('WENDI-2 relative dose response')
ax.set_title('WENDI-2 Over/Under-Response Relative to $H^*(10)$')
ax.grid(True, which="both", ls="--", alpha=0.5)
ax.legend()

# Save the new independent plot
plt.tight_layout()
plt.savefig('wendi2_to_h10_ratio.png', dpi=300)
plt.close(fig)

# Create two overimposed plots to compare the neutron fluence and the WENDI2 relative response
# Create a figure with 2 rows, 1 column, sharing the X-axis
# gridspec_kw is used to make the top plot larger than the bottom ratio plot
fig, (ax_top, ax_bottom) = plt.subplots(
    2, 1,
    figsize=(9, 8),
    sharex=True,
    gridspec_kw={'height_ratios': [2.5, 1]}
)

# --- Top Pad: Fluence Spectrum ---
ax_top.plot(E_center, fluence, color='blue', label='Neutron Fluence', linestyle='-', marker='.')
ax_top.set_yscale('log')
ax_top.set_ylabel('Fluence (particles/$cm^2$)', fontsize=12)
ax_top.set_title('Simulated Neutron Spectrum (SwissFEL) & WENDI-2 Relative Response', fontsize=14, pad=15)
ax_top.grid(True, which="both", ls="--", alpha=0.5)
ax_top.legend(loc='upper right')

# Remove the bottom X-axis tick labels for the top pad to avoid visual overlap
ax_top.tick_params(axis='x', labelbottom=False)

# --- Bottom Pad: WENDI-2 Ratio ---
# We use a log scale for both axes here as well
ax_bottom.loglog(x_wendi, ratio, color='purple', label='WENDI-2 / $H^*(10)$', lw=2)
ax_bottom.axhline(1.0, color='red', linestyle='-', alpha=0.8, label='Ideal (Ratio = 1.0)')

ax_bottom.set_xlabel('Energy ($MeV$)', fontsize=12)
ax_bottom.set_ylabel('Response Ratio', fontsize=12)
ax_bottom.grid(True, which="both", ls="--", alpha=0.5)
ax_bottom.legend(loc='upper left')

# Adjust layout to minimize the vertical space (hspace) between the two plots
plt.subplots_adjust(hspace=0.05)

# Save the figure
plt.savefig('stacked_fluence_and_ratio.png', dpi=300, bbox_inches='tight')
plt.close(fig)

# --- GLOBAL BIAS CALCULATION (WENDI-2 Over/Under-response for SwissFEL Neutron Spectrum) ---

from scipy.interpolate import interp1d

# 1. We already have the ratio array calculated on the WENDI energy grid (x_wendi).
# Now, we need to interpolate this ratio onto the neutron fluence energy grid (E_center).
# We use log-log interpolation to preserve the physical shape over multiple decades.
log_ratio = np.log10(ratio)
f_interp_ratio_log = interp1d(
    np.log10(x_wendi), 
    log_ratio, 
    kind='linear', 
    bounds_error=False, 
    fill_value="extrapolate" # Allows calculation even if spectrum exceeds WENDI limits
)

# Evaluate the interpolation function at our simulated energy bins
ratio_interp = 10**(f_interp_ratio_log(np.log10(E_center)))

# 2. We must do the exact same log-log interpolation for the ICRP H*(10) conversion factors.
# We map y_h10 (which is on x_h10 grid) onto our E_center grid.
f_interp_h10_log = interp1d(
    np.log10(x_h10),
    np.log10(y_h10),
    kind='linear',
    bounds_error=False,
    fill_value="extrapolate"
)

h10_interp = 10**(f_interp_h10_log(np.log10(E_center)))

# 3. FOLDING: Calculate the dose for each energy bin
# 'fluence' is already integrated per bin (dN_dE * dE) so its unit is [neutrons / cm^2]
# 'h10_interp' unit is [pSv * cm^2]
# The product directly yields the absolute dose [pSv] per bin.

# The "True" expected environmental dose
ideal_dose_spectrum = fluence * h10_interp

# The Dose that the WENDI-2 would actually register, skewed by its response ratio
measured_dose_spectrum = fluence * h10_interp * ratio_interp

# 4. Integrate (sum) over the entire spectrum
# We use np.nansum to safely ignore any potential NaN values from extreme extrapolations
total_ideal_dose = np.nansum(ideal_dose_spectrum)
total_measured_dose = np.nansum(measured_dose_spectrum)

# 5. Calculate the global correction factor for this specific environment
global_bias = total_measured_dose / total_ideal_dose

print("\n--- DOSIMETRY RESULTS ---")
print(f"Total Ideal Expected Dose: {total_ideal_dose:.3e} pSv")
print(f"Total WENDI-2 Measured Dose: {total_measured_dose:.3e} pSv")
print(f"Global Correction Factor (Bias): {global_bias:.3f}")

if global_bias < 1.0:
    print(f"-> The WENDI-2 UNDER-RESPONDS by {(1.0 - global_bias)*100:.1f}%.")
    print(f"-> Field measurements must be multiplied by {1.0/global_bias:.3f} to find the true H*(10).")
else:
    print(f"-> The WENDI-2 OVER-RESPONDS by {(global_bias - 1.0)*100:.1f}%.")

# --- 6. FINAL DIAGNOSTIC STACKED PLOT FOR NEUTRONS (Fluence, H*(10), Ratio) ---
# Create a figure with 3 subplots stacked vertically, sharing the X-axis.
fig_diag, axs = plt.subplots(3, 1, figsize=(10, 10), sharex=True, gridspec_kw={'height_ratios': [2, 1.5, 1.5]})

# --- Plot 1: Neutron Fluence Spectrum ---
# Using 'E_center' and 'fluence' directly since no zero-filtering is needed for neutrons
axs[0].plot(E_center, fluence, color='blue', marker='.', linestyle='-', label='Neutron Fluence')
axs[0].set_yscale('log')
axs[0].set_ylabel('Fluence ($particles/cm^2$)', fontsize=11)
axs[0].set_title('Dosimetric Analysis Pipeline for Neutrons at SwissFEL', fontsize=14, pad=15)
axs[0].grid(True, which="both", ls="--", alpha=0.5)
axs[0].legend(loc='upper right')

# Remove bottom ticks to avoid visual overlap
axs[0].tick_params(axis='x', labelbottom=False)

# --- Plot 2: Interpolated H*(10) Conversion Factors ---
# Using log scale for Y-axis since neutron H*(10) coefficients are strictly positive 
# across the entire energy spectrum (unlike electrons/positrons)
axs[1].plot(E_center, h10_interp, color='darkorange', linestyle='-', linewidth=2, label='ICRP 74 $H^*(10)$ Conversion')
axs[1].set_yscale('log')
axs[1].set_ylabel(r'$H^*(10)/\Phi$ ($pSv \cdot cm^2$)', fontsize=11)
axs[1].grid(True, which="both", ls="--", alpha=0.5)
axs[1].legend(loc='upper left')
axs[1].tick_params(axis='x', labelbottom=False)

# --- Plot 3: Interpolated WENDI-2 Relative Response ---
# Note: 'ratio_interp' holds the WENDI-2 relative response ratio interpolated on 'E_center'
axs[2].plot(E_center, ratio_interp, color='purple', linestyle='-', linewidth=2, label='WENDI-2 Relative Response')
axs[2].axhline(1.0, color='red', linestyle='--', alpha=0.8, label='Ideal Response (1.0)')
axs[2].set_xscale('log') 
axs[2].set_xlabel('Energy ($MeV$)', fontsize=12)
axs[2].set_ylabel('Measured / Ideal', fontsize=11)
axs[2].grid(True, which="both", ls="--", alpha=0.5)
axs[2].legend(loc='upper left')

# Adjust layout to stick the three panels together
plt.subplots_adjust(hspace=0.05)

# Save the diagnostic plot
diag_filename = 'diagnostic_pipeline_neutrons.png'
plt.savefig(diag_filename, dpi=300, bbox_inches='tight')
plt.close(fig_diag)
print(f"Diagnostic 3-panel plot saved as '{diag_filename}'.")
