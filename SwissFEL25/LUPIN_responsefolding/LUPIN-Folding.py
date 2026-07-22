import numpy as np

# This is the lower side of the energy bin from FLUKA for neutron spectrum at position 5, highest position of LUPIN detector during 2025 SwissFEL data taking.
# Energies in GeV.
neutron_flux_bin_min = [1.0000000E-12,1.1271975E-12,1.2705742E-12,1.4321880E-12,1.6143588E-12,1.8197013E-12,2.0511626E-12,2.3120653E-12,2.6061542E-12,2.9376503E-12,3.3113124E-12,3.7325030E-12,4.2072678E-12,4.7424222E-12,5.3456462E-12,6.0255989E-12,6.7920400E-12,7.6559705E-12,8.6297905E-12,9.7274784E-12,1.0964789E-11,1.2359482E-11,1.3931579E-11,1.5703640E-11,1.7701103E-11,1.9952638E-11,2.2490567E-11,2.5351308E-11,2.8575930E-11,3.2210720E-11,3.6307842E-11,4.0926110E-11,4.6131807E-11,5.1999658E-11,5.8613885E-11,6.6069421E-11,7.4473282E-11,8.3946100E-11,9.4623837E-11,1.0665975E-10,1.2022661E-10,1.3551912E-10,1.5275682E-10,1.7218710E-10,1.9408886E-10,2.1877648E-10,2.4660432E-10,2.7797176E-10,3.1332906E-10,3.5318373E-10,3.9810782E-10,4.4874612E-10,5.0582555E-10,5.7016530E-10,6.4268890E-10,7.2443723E-10,8.1658386E-10,9.2045122E-10,1.0375304E-09,1.1695016E-09,1.3182593E-09,1.4859387E-09,1.6749463E-09,1.8879953E-09,2.1281434E-09,2.3988380E-09,2.7039644E-09,3.0479019E-09,3.4355871E-09,3.8725854E-09,4.3651691E-09,4.9204072E-09,5.5462706E-09,6.2517418E-09,7.0469484E-09,7.9433020E-09,8.9536698E-09,1.0092554E-08,1.1376303E-08,1.2823340E-08,1.4454436E-08,1.6293004E-08,1.8365434E-08,2.0701469E-08,2.3334646E-08,2.6302754E-08,2.9648398E-08,3.3419603E-08,3.7670489E-08,4.2462077E-08,4.7863153E-08,5.3951222E-08,6.0813683E-08,6.8549042E-08,7.7268297E-08,8.7096630E-08,9.8175100E-08,1.1066273E-07,1.2473876E-07,1.4060521E-07,1.5848983E-07,1.7864934E-07,2.0137311E-07,2.2698727E-07,2.5585948E-07,2.8840412E-07,3.2508845E-07,3.6643888E-07,4.1304892E-07,4.6558779E-07,5.2480937E-07,5.9156383E-07,6.6680923E-07,7.5162569E-07,8.4723058E-07,9.5499615E-07,1.0764694E-06,1.2133936E-06,1.3677343E-06,1.5417065E-06,1.7378076E-06,1.9588524E-06,2.2080135E-06,2.4888673E-06,2.8054451E-06,3.1622910E-06,3.5645262E-06,4.0179252E-06,4.5289949E-06,5.1050720E-06,5.7544244E-06,6.4863725E-06,7.3114229E-06,8.2414172E-06,9.2897062E-06,1.0471332E-05,1.1803259E-05,1.3304604E-05,1.4996917E-05,1.6904489E-05,1.9054694E-05,2.1478407E-05,2.4210405E-05,2.7289909E-05,3.0761115E-05,3.4673852E-05,3.9084276E-05,4.4055701E-05,4.9659477E-05,5.5976037E-05,6.3096049E-05,7.1121707E-05,8.0168211E-05,9.0365400E-05,1.0185967E-04,1.1481595E-04,1.2942024E-04,1.4588219E-04,1.6443802E-04,1.8535415E-04,2.0893072E-04,2.3550619E-04,2.6546197E-04,2.9922806E-04,3.3728912E-04,3.8019146E-04,4.2855091E-04,4.8306148E-04,5.4450566E-04,6.1376544E-04,6.9183490E-04,7.7983458E-04,8.7902747E-04,9.9083758E-04,1.1168697E-03,1.2589328E-03,1.4190659E-03,1.5995674E-03,1.8030284E-03,2.0323689E-03,2.2908812E-03,2.5822758E-03,2.9107349E-03,3.2809728E-03,3.6983043E-03,4.1687191E-03,4.6989699E-03,5.2966666E-03,5.9703896E-03,6.7298091E-03,7.5858231E-03,8.5507212E-03,9.6383514E-03,1.0864326E-02,1.2246241E-02,1.3803933E-02,1.5559757E-02,1.7538920E-02,1.9769827E-02,2.2284498E-02,2.5119031E-02,2.8314108E-02,3.1915594E-02,3.5975177E-02,4.0551126E-02,4.5709126E-02,5.1523220E-02,5.8076844E-02,6.5464064E-02,7.3790938E-02,8.3176956E-02,9.3756847E-02,0.1056825,0.1191250,0.1342774,0.1513572,0.1706095,0.1923105,0.2167720,0.2443448,0.2754248,0.3104582,0.3499477,0.3944602,0.4446345,0.5011910,0.5649412,0.6368003,0.7177996,0.8091020,0.9120178,1.028024,1.158786,1.306181,1.472324,1.659600,1.870697,2.108645,2.376859,2.679189,3.019976,3.404109,3.837103,4.325173,4.875324,5.495454,6.194462,6.982381,7.870522,8.871633]
neutron_flux_bin_min = [x*1000 for x in neutron_flux_bin_min] # convert GeV to MeV

# This is the upper side of the energy bin from FLUKA for neutron spectrum at position 5, highest position of LUPIN detector during 2025 SwissFEL data taking.
# Energies in GeV.
neutron_flux_bin_max = [1.1271975E-12,1.2705742E-12,1.4321880E-12,1.6143588E-12,1.8197013E-12,2.0511626E-12,2.3120653E-12,2.6061542E-12,2.9376503E-12,3.3113124E-12,3.7325030E-12,4.2072678E-12,4.7424222E-12,5.3456462E-12,6.0255989E-12,6.7920400E-12,7.6559705E-12,8.6297905E-12,9.7274784E-12,1.0964789E-11,1.2359482E-11,1.3931579E-11,1.5703640E-11,1.7701103E-11,1.9952638E-11,2.2490567E-11,2.5351308E-11,2.8575930E-11,3.2210720E-11,3.6307842E-11,4.0926110E-11,4.6131807E-11,5.1999658E-11,5.8613885E-11,6.6069421E-11,7.4473282E-11,8.3946100E-11,9.4623837E-11,1.0665975E-10,1.2022661E-10,1.3551912E-10,1.5275682E-10,1.7218710E-10,1.9408886E-10,2.1877648E-10,2.4660432E-10,2.7797176E-10,3.1332906E-10,3.5318373E-10,3.9810782E-10,4.4874612E-10,5.0582555E-10,5.7016530E-10,6.4268890E-10,7.2443723E-10,8.1658386E-10,9.2045122E-10,1.0375304E-09,1.1695016E-09,1.3182593E-09,1.4859387E-09,1.6749463E-09,1.8879953E-09,2.1281434E-09,2.3988380E-09,2.7039644E-09,3.0479019E-09,3.4355871E-09,3.8725854E-09,4.3651691E-09,4.9204072E-09,5.5462706E-09,6.2517418E-09,7.0469484E-09,7.9433020E-09,8.9536698E-09,1.0092554E-08,1.1376303E-08,1.2823340E-08,1.4454436E-08,1.6293004E-08,1.8365434E-08,2.0701469E-08,2.3334646E-08,2.6302754E-08,2.9648398E-08,3.3419603E-08,3.7670489E-08,4.2462077E-08,4.7863153E-08,5.3951222E-08,6.0813683E-08,6.8549042E-08,7.7268297E-08,8.7096630E-08,9.8175100E-08,1.1066273E-07,1.2473876E-07,1.4060521E-07,1.5848983E-07,1.7864934E-07,2.0137311E-07,2.2698727E-07,2.5585948E-07,2.8840412E-07,3.2508845E-07,3.6643888E-07,4.1304892E-07,4.6558779E-07,5.2480937E-07,5.9156383E-07,6.6680923E-07,7.5162569E-07,8.4723058E-07,9.5499615E-07,1.0764694E-06,1.2133936E-06,1.3677343E-06,1.5417065E-06,1.7378076E-06,1.9588524E-06,2.2080135E-06,2.4888673E-06,2.8054451E-06,3.1622910E-06,3.5645262E-06,4.0179252E-06,4.5289949E-06,5.1050720E-06,5.7544244E-06,6.4863725E-06,7.3114229E-06,8.2414172E-06,9.2897062E-06,1.0471332E-05,1.1803259E-05,1.3304604E-05,1.4996917E-05,1.6904489E-05,1.9054694E-05,2.1478407E-05,2.4210405E-05,2.7289909E-05,3.0761115E-05,3.4673852E-05,3.9084276E-05,4.4055701E-05,4.9659477E-05,5.5976037E-05,6.3096049E-05,7.1121707E-05,8.0168211E-05,9.0365400E-05,1.0185967E-04,1.1481595E-04,1.2942024E-04,1.4588219E-04,1.6443802E-04,1.8535415E-04,2.0893072E-04,2.3550619E-04,2.6546197E-04,2.9922806E-04,3.3728912E-04,3.8019146E-04,4.2855091E-04,4.8306148E-04,5.4450566E-04,6.1376544E-04,6.9183490E-04,7.7983458E-04,8.7902747E-04,9.9083758E-04,1.1168697E-03,1.2589328E-03,1.4190659E-03,1.5995674E-03,1.8030284E-03,2.0323689E-03,2.2908812E-03,2.5822758E-03,2.9107349E-03,3.2809728E-03,3.6983043E-03,4.1687191E-03,4.6989699E-03,5.2966666E-03,5.9703896E-03,6.7298091E-03,7.5858231E-03,8.5507212E-03,9.6383514E-03,1.0864326E-02,1.2246241E-02,1.3803933E-02,1.5559757E-02,1.7538920E-02,1.9769827E-02,2.2284498E-02,2.5119031E-02,2.8314108E-02,3.1915594E-02,3.5975177E-02,4.0551126E-02,4.5709126E-02,5.1523220E-02,5.8076844E-02,6.5464064E-02,7.3790938E-02,8.3176956E-02,9.3756847E-02,0.1056825,0.1191250,0.1342774,0.1513572,0.1706095,0.1923105,0.2167720,0.2443448,0.2754248,0.3104582,0.3499477,0.3944602,0.4446345,0.5011910,0.5649412,0.6368003,0.7177996,0.8091020,0.9120178,1.028024,1.158786,1.306181,1.472324,1.659600,1.870697,2.108645,2.376859,2.679189,3.019976,3.404109,3.837103,4.325173,4.875324,5.495454,6.194462,6.982381,7.870522,8.871633,10.00008]
neutron_flux_bin_max = [x*1000 for x in neutron_flux_bin_max] # convert GeV to MeV

# This is the differential fluence of the neutrons (dN/dE) (Neutrons/GeVcm2) simulated with FLUKA in 2025, at position 5
neutron_fluence_differential = [117246.2,233992.5,534151.0,866435.8,603607.4,636633.0,723700.0,767987.1,895420.3,999605.8,1025595.,1632460.,1454233.,1650087.,2122105.,2203680.,2676643.,2726362.,2972709.,3216134.,3856352.,3762621.,4761256.,4807833.,4940444.,5562848.,5963586.,6105506.,6275949.,6350830.,5997725.,5941313.,5384315.,5025278.,4368488.,3709784.,3131228.,2413154.,1833544.,1325806.,926296.3,615196.2,407450.5,217857.1,155178.8,98021.43,83679.08,51679.01,51006.27,41530.21,32918.08,37520.00,23968.84,23251.12,18903.23,16662.23,14919.78,10121.87,11802.58,9424.813,7682.492,6118.555,5988.596,5378.093,4403.139,3213.270,3549.892,2826.415,2519.545,2394.752,2014.207,1576.666,1495.322,1566.933,1050.101,1132.869,791.5505,886.7409,527.4958,431.6891,427.1064,417.7705,326.3943,322.9293,275.8129,237.2537,217.5544,192.2110,167.9964,163.8302,127.7357,119.6830,82.11761,82.72034,61.01040,54.68556,63.35694,44.63813,44.28531,38.96105,33.37617,25.17617,21.69421,18.36428,16.79788,13.76502,10.72184,12.68534,9.619267,8.443299,8.690833,6.968849,5.545775,5.173352,3.741765,3.705240,3.460905,3.634304,3.593102,2.468671,1.857929,1.834653,1.610913,1.031667,0.5825723,0.9025270,0.8222470,0.6620001,0.6893918,0.6788666,0.3592639,0.4414320,0.3817325,0.2306036,0.2545180,0.2759129,0.1737765,0.1721908,0.1865699,0.1846059,0.1135198,0.1036822,7.1213663E-02,8.1867680E-02,7.6343767E-02,5.1079903E-02,5.3637858E-02,5.0663520E-02,4.1053507E-02,3.4540571E-02,3.6716688E-02,2.7149525E-02,1.8635528E-02,1.7936349E-02,1.8129811E-02,1.5753603E-02,1.3491048E-02,1.1520599E-02,9.4447834E-03,7.1753166E-03,8.8050570E-03,7.0950021E-03,5.4679015E-03,4.7118026E-03,2.6721535E-03,2.2567345E-03,3.1256853E-03,3.8535905E-03,3.4560761E-03,2.4349410E-03,2.4248997E-03,1.6445641E-03,8.6716883E-04,8.7608671E-04,1.5213244E-03,9.8799856E-04,9.2968624E-04,9.5190608E-04,7.9225504E-04,9.2056225E-04,1.1145205E-03,6.6296471E-04,4.8704544E-04,2.9227309E-04,3.2028562E-04,2.9280386E-04,2.6337302E-04,2.0406746E-04,1.9437737E-04,1.3303374E-04,1.0736549E-04,1.0108003E-04,8.0492006E-05,6.4176602E-05,6.3598534E-05,5.7583293E-05,5.8338363E-05,5.8042711E-05,5.0058185E-05,4.6317462E-05,5.0774022E-05,4.9038223E-05,5.0460607E-05,4.8514263E-05,4.8638103E-05,5.3446598E-05,5.0306549E-05,4.7739919E-05,4.2394768E-05,3.7047117E-05,3.2238917E-05,2.8675748E-05,2.4428526E-05,2.2240047E-05,1.8539540E-05,1.4749735E-05,1.1264682E-05,7.3882052E-06,5.3803233E-06,3.3964413E-06,2.0080213E-06,1.2923995E-06,8.8022892E-07,3.9606729E-07,2.3422587E-07,1.5961994E-07,9.4918988E-08,3.5668730E-08,2.3481862E-08,8.1235241E-09,5.7362026E-09,2.7485951E-09,6.2520877E-10,6.3198918E-10,9.8037342E-11,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000]

print("Entries for neutron flux lower energggy bin side :", len(neutron_flux_bin_min))
print("Entries for neutron flux upper energy bin side :", len(neutron_flux_bin_max))
print("Entries for neutron flux differential fluence :",  len(neutron_fluence_differential))

# --- Plot the neutron fluence (particles/cm2) and neutron differential fluence (particles/cm2MeV) ---

import matplotlib.pyplot as plt
import numpy as np

E_min = np.array(neutron_flux_bin_min) # convert to numpy array
E_max = np.array(neutron_flux_bin_max)
dN_dE = np.array(neutron_fluence_differential) / 1000.0 # convert GeV to MeV

dE = E_max - E_min # the width of each energy bin

fluence = dN_dE * dE # to get the fluence (neutrons/cm^2) I have to multiply my values for the bin width

E_center = np.sqrt(E_min * E_max) # the geometric mean for log-scaled bin centers

# The lethargy (E * dN/dE)
# Both E_center and the denominator of dN_dE are in MeV
lethargy = dN_dE * (E_center) # the lethargy 

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
plt.savefig('neutron_fluence_plot_pos5.png', dpi=300)

# This is the fluence to H*(10) convertion function in pSVcm2, energy bins in MeV
# Numbers are taken from "MCNPX SIMULATIONS OF THE RESPONSE OF THE EXTENDED-RANGE REM METER WENDI-2", DOI:10.2298/NTRP140SS25S
#energy_fluence_to_H10_function = [9.492218410280988e-9, 7.79370003310337e-8, 1.8450523636359488e-7, 6.391572541760222e-7, 0.000001196590178695872, 0.0000027823102149957592, 0.000005307285683717842, 0.000010231106652003436, 0.000023278138167773893, 0.000042483917203395035, 0.00008076191527801742, 0.00018928383651851429, 0.0003635068849352923, 0.0006903189177272841, 0.0015915557824633265, 0.002983585657778197, 0.005645429347979109, 0.012824224181601233, 0.02477975812960878, 0.04713481248081918, 0.06763915344644195, 0.11162795508530567, 0.14910430495168958, 0.2021168295695759, 0.2825530174737817, 0.3761227679543664, 0.5621630080012422, 0.8581092921177734, 1.193311490116029, 1.9315797200635523, 3.0635427165248004, 5.924792950263549, 10.620032233831877, 15.879348937441032, 25.5432651555736, 37.24580147079381, 60.24223934384477, 92.0448653985943, 117.69899660418108, 169.5378901352275, 315.4687877287317, 401.7072772240769, 484.8280013467348, 592.2872514265484, 775.1935095763772, 938.3016521377199, 1371.130530716348, 1805.7079793741932, 2623.723141019056, 4015.405527485102]

#fluence_to_H10_function = [6.466250424686161, 8.799679730059975, 10.311071254352676, 12.550073554335057, 13.110995769306358, 13.04732071640402, 12.938089587841061, 12.36783915759269, 11.533934092774762, 10.919057066048893, 10.306481384258957, 9.570783817289552, 9.149872743451809, 8.556373881792219, 8.014033284880584, 7.680080716074246, 7.548324338039095, 7.711408181310479, 10.092721735729185, 15.751225781458523, 22.92952436337824, 39.43955380203264, 58.34955046204815, 85.68835482460437, 129.1868168874242, 168.6254770987624, 231.96883530095405, 318.4074658501491, 370.05932308196606, 419.7154323430968, 416.52189589866686, 404.15489820942605, 400.77134563145006, 470.27585035359493, 592.2088584676992, 515.0339239286063, 405.1138282879553, 319.4097514591874, 283.28833951915, 242.9008838853542, 303.56107190068565, 343.66199531090075, 413.0752985273366, 478.6141706126125, 562.9223957316359, 651.3011760820857, 723.0153836888301, 790.8497596100315, 854.9824782620643, 935.9175337863275]

# --- ICRP 74 standard reference values for neutrons ---
icrp74_energy_mev = np.array([
    1.00e-09, 1.00e-08, 2.53e-08, 1.00e-07, 2.00e-07, 5.00e-07, 1.00e-06,
    2.00e-06, 5.00e-06, 1.00e-05, 2.00e-05, 5.00e-05, 1.00e-04, 2.00e-04,
    5.00e-04, 1.00e-03, 2.00e-03, 5.00e-03, 1.00e-02, 2.00e-02, 3.00e-02,
    5.00e-02, 7.00e-02, 1.00e-01, 1.50e-01, 2.00e-01, 3.00e-01, 5.00e-01,
    7.00e-01, 9.00e-01, 1.00e+00, 1.20e+00, 2.00e+00, 3.00e+00, 4.00e+00,
    5.00e+00, 6.00e+00, 7.00e+00, 8.00e+00, 9.00e+00, 1.00e+01, 1.20e+01,
    1.40e+01, 1.50e+01, 1.60e+01, 1.80e+01, 2.00e+01, 3.00e+01, 5.00e+01,
    7.50e+01, 1.00e+02, 1.25e+02, 1.50e+02, 1.75e+02, 2.01e+02
])

icrp74_h10_sv_cm2 = np.array([
    6.60e-12, 9.00e-12, 1.06e-11, 1.29e-11, 1.35e-11, 1.36e-11, 1.33e-11,
    1.29e-11, 1.20e-11, 1.13e-11, 1.06e-11, 9.90e-12, 9.40e-12, 8.90e-12,
    8.30e-12, 7.90e-12, 7.70e-12, 8.00e-12, 1.05e-11, 1.66e-11, 2.37e-11,
    4.11e-11, 6.00e-11, 8.80e-11, 1.32e-10, 1.70e-10, 2.33e-10, 3.22e-10,
    3.75e-10, 4.00e-10, 4.16e-10, 4.25e-10, 4.20e-10, 4.12e-10, 4.08e-10,
    4.05e-10, 4.00e-10, 4.05e-10, 4.09e-10, 4.20e-10, 4.40e-10, 4.80e-10,
    5.20e-10, 5.40e-10, 5.55e-10, 5.70e-10, 6.00e-10, 5.15e-10, 4.00e-10,
    3.30e-10, 2.85e-10, 2.60e-10, 2.45e-10, 2.50e-10, 2.60e-10
])

# --- Pelliccioni high-energy extension values for neutrons ---
pelliccioni_energy_mev = np.array([
    2.5e-08, 1.0e-03, 1.0e-01, 1.0e+00, 5.0e+00, 1.0e+01, 1.5e+01, 1.9e+01,
    2.0e+01, 5.0e+01, 1.0e+02, 2.0e+02, 5.0e+02, 1.0e+03, 5.0e+03, 1.0e+04,
    1.0e+05, 1.0e+06, 1.0e+07
])

pelliccioni_h10_sv_cm2 = np.array([
    1.04e-11, 8.62e-12, 1.08e-10, 4.92e-10, 4.26e-10, 4.63e-10, 5.08e-10,
    5.56e-10, 5.26e-10, 3.59e-10, 2.62e-10, 2.21e-10, 2.90e-10, 3.77e-10,
    4.92e-10, 5.23e-10, 4.99e-10, 7.17e-10, 1.16e-09
])

# --- Merge datasets: ICRP74 up to 20 MeV, Pelliccioni above 20 MeV ---
# Filter ICRP74 data up to 20.0 MeV (inclusive)
icrp_mask = icrp74_energy_mev <= 20.0

# Filter Pelliccioni data strictly above 20.0 MeV
pell_mask = pelliccioni_energy_mev > 20.0

icru_energy_mev = np.concatenate([
    icrp74_energy_mev[icrp_mask], 
    pelliccioni_energy_mev[pell_mask]
])

icru_h10_sv_cm2 = np.concatenate([
    icrp74_h10_sv_cm2[icrp_mask], 
    pelliccioni_h10_sv_cm2[pell_mask]
])

# --- Convert Sv * cm^2 to pSv * cm^2 (1 Sv = 1e12 pSv) ---
icru_h10_psv_cm2 = icru_h10_sv_cm2 * 1e12

energy_fluence_to_H10_function = icru_energy_mev
fluence_to_H10_function = icru_h10_psv_cm2

# --- Plot the Fluence-to-H*(10) Conversion Function ---
plt.figure(figsize=(10, 5))

# Plot the merged conversion function (ICRP 74 + Pelliccioni)
plt.plot(energy_fluence_to_H10_function, fluence_to_H10_function,
         color='forestgreen', marker='o', linestyle='-', linewidth=1.5, label='Merged ICRU H*(10)')

# Highlight the transition point at 20 MeV
plt.axvline(20.0, color='red', linestyle='--', alpha=0.7, label='Transition ICRP 74 / Pelliccioni (20 MeV)')

plt.xscale('log')
plt.yscale('log')
plt.xlabel('Energy (MeV)', fontsize=11)
plt.ylabel('H*(10) Conversion Factor (pSv cm^2)', fontsize=11)
plt.grid(True, which="both", linestyle="--", alpha=0.5)
plt.legend(loc='lower right')
plt.title('Fluence-to-H*(10) Dose Conversion Function', fontsize=13, pad=10)
plt.tight_layout()
plt.savefig('fluence_to_H10_conversion_function.png', dpi=300)
plt.close()

# LUPIN incident neutron energy values in MeV
# Data from "Experimental characterization of the LUPIN Rem counter in monoenergetic neutron fields"
lupin_energies_MeV = np.array([
    1.2399521979954246e-08, 2.3161778823663442e-08, 4.2058902393143640e-08,
    7.1720950834541420e-08, 1.0444115508974373e-07, 1.5019215840545002e-07,
    2.2428229566950033e-07, 2.9951177848859005e-07, 3.7384303927064850e-07,
    5.6840713830525310e-07, 9.5125791085664130e-07, 1.5974124667154441e-06,
    2.2960410845841200e-06, 4.0543785261151460e-06, 5.8022868798773260e-06,
    9.2064032734871490e-06, 1.3707429331742728e-05, 1.9683391585088578e-05,
    2.8623292770622490e-05, 4.2234824698464686e-05, 5.7687836090952030e-05,
    9.6242709894158960e-05, 1.3936773929573930e-04, 2.1610082443151480e-04,
    3.6620408307974730e-04, 4.8697818047945175e-04, 7.6924534348640500e-04,
    1.2429021060606164e-03, 1.7117573905817026e-03, 2.8478528367764052e-03,
    4.3345781180527026e-03, 6.1220931888430880e-03, 8.9796256646473110e-03,
    1.1326765936585497e-02, 1.4496740753352975e-02, 1.7810131054788788e-02,
    2.1743786125671700e-02, 2.5844748795371783e-02, 3.5147506072333100e-02,
    3.8957991503991320e-02, 4.2687818431757250e-02, 4.7691775764906080e-02,
    5.4925128774250605e-02, 6.3786259393291800e-02, 7.2039581159786730e-02,
    9.3091771097431070e-02, 1.0640793217345643e-01, 1.2793875509771438e-01,
    1.5696141157058680e-01, 2.1645856288322202e-01, 3.5513550974892850e-01,
    5.6153326159295060e-01, 7.8684846002721030e-01, 1.1161833869690025e+00,
    1.5784415993064644e+00, 2.1948733897193580e+00, 3.5237499922465076e+00,
    4.5137807483391070e+00, 6.1247651215626915e+00, 7.4653876704898370e+00,
    8.9903084101821470e+00, 10.226639359623325e+00, 12.588936875036845e+00,
    14.762418038803625e+00, 17.134199456753592e+00, 23.340662484371066e+00,
    36.026370234908510e+00, 50.697562158594515e+00, 66.896287022267370e+00,
    86.379681745681400e+00, 108.13926059603165e+00, 140.07689559485050e+00,
    181.01168955759620e+00, 228.20190927196910e+00, 284.56140596750345e+00,
    334.96601983581530e+00, 448.24152919168785e+00, 674.67918864405190e+00,
    848.81660732296070e+00
])
# LUPIN ratio response (neutron response / ICRU dose-to-fluence conversion factor)
# Data from "Experimental characterization of the LUPIN Rem counter in monoenergetic neutron fields"
lupin_ratio_response = np.array([
    0.8277104565456144, 0.8080673626964476, 0.8420429595657015,
    0.9103889121960161, 0.9823645064518193, 1.0822646653809902,
    1.1436551408402570, 1.2343367063474250, 1.3161330516606928,
    1.4153550709396627, 1.5861600077094353, 1.7583998910757013,
    1.9222463102630833, 2.1168746863772894, 2.3084900673841258,
    2.5198000654498170, 2.6910066441091005, 2.8980665202627400,
    3.0740370429500805, 3.2550352063588740, 3.4771934694487800,
    3.7452211366059283, 3.9068254090704566, 4.3297823951897625,
    4.5705212180394240, 4.9709276511563450, 5.2147627127828100,
    5.6281420256372360, 5.9646408778697940, 6.1426542857137720,
    6.2336457033036300, 5.9408945135408080, 5.3556200098497220,
    4.7832387734044780, 4.1893160842691330, 3.7611777818736516,
    3.3162875378778380, 2.9362237398574210, 2.6647062970049102,
    2.4494871740031860, 2.1500781081448963, 1.9122263168748599,
    1.6289216194715583, 1.4626085996828250, 1.3339700258562326,
    1.2027090153770320, 1.0733689875086279, 0.9731913063393467,
    0.9020062849205753, 0.8024831354918666, 0.7410957271275447,
    0.7868029989660709, 0.8447493054391123, 0.9303818659031696,
    1.0631801489925863, 1.1722607198292088, 1.1050795647484006,
    1.1777540685534063, 1.1070792332684850, 1.0084238081187700,
    0.8681367114380607, 0.7847695439195383, 0.6577248121379508,
    0.5731279482206664, 0.5129440083928957, 0.45888418590984126,
    0.4625795795992287, 0.5374224858036324, 0.6092668413919866,
    0.7067593948367860, 0.8270445050573277, 0.9502350745073649,
    1.0254597392025826, 0.9267661583808423, 0.8392458247887523,
    0.7624849207027067, 0.6820925516030660, 0.7191230350418380,
    0.7105233980818508
])

from scipy.interpolate import interp1d

# ==============================================================================
# DATA PREPARATION & INTERPOLATION
# ==============================================================================
# Convert lists to numpy arrays for interpolation routines
icru_energies = np.array(energy_fluence_to_H10_function)
icru_factors = np.array(fluence_to_H10_function)

# Interpolate ICRU conversion factors.
# Using log-log interpolation because both energy and conversion factors
# span multiple orders of magnitude. For energies outside the ICRU vector bounds
# (e.g., above 4 GeV or below 9.5e-9 MeV), we hold the edge values constant.
interp_icru_log = interp1d(
    np.log10(icru_energies),
    np.log10(icru_factors),
    kind='linear',
    bounds_error=False,
    fill_value=(np.log10(icru_factors[0]), np.log10(icru_factors[-1]))
)

# Wrapper to safely convert back from log space
def get_icru_factor(e):
    return 10**(interp_icru_log(np.log10(e)))

# Interpolate LUPIN ratio response.
# Using log-linear interpolation because the ratio fluctuates linearly around 1,
# but the X-axis (energy) spans decades. Edge values are held constant for extrapolations.
interp_lupin_ratio = interp1d(
    np.log10(lupin_energies_MeV),
    lupin_ratio_response,
    kind='linear',
    bounds_error=False,
    fill_value=(lupin_ratio_response[0], lupin_ratio_response[-1])
)

def get_lupin_ratio(e):
    return interp_lupin_ratio(np.log10(e))

# ==============================================================================
# DOSE AND CORRECTION FACTOR CALCULATION
# ==============================================================================
# Evaluate reference data at the simulated FLUKA bin centers (E_center)
icru_at_sim_energies = get_icru_factor(E_center)
lupin_ratio_at_sim_energies = get_lupin_ratio(E_center)

# Calculate the "True" ambient dose equivalent H*(10) per bin (in pSv)
# Formula: Fluence (cm^-2) * Conversion Factor (pSv * cm^2)
true_dose_per_bin = fluence * icru_at_sim_energies
total_true_dose = np.sum(true_dose_per_bin)

# Calculate the LUPIN estimated ambient dose equivalent H*(10) per bin (in pSv)
# Formula: True Dose per bin * LUPIN Response Ratio
lupin_dose_per_bin = true_dose_per_bin * lupin_ratio_at_sim_energies
total_lupin_dose = np.sum(lupin_dose_per_bin)

# Calculate the final correction factor for the LUPIN detector
# If LUPIN overestimates the dose, C < 1. If it underestimates, C > 1.
lupin_correction_factor = total_true_dose / total_lupin_dose

# Created a debug plot with interpolated curves
# Create the figure and the first y-axis (for Fluence)
fig, ax1 = plt.subplots(figsize=(9, 6))

# Plot Fluence on the left y-axis
color_fluence = 'tab:blue'
ax1.set_xlabel('Energy $E_{center}$ [MeV]') # Adjust unit if it is eV or GeV
ax1.set_ylabel('Fluence [cm$^{-2}$]', color=color_fluence)

# Using step plot since fluence is typically binned, or plot if it is a smooth curve
line1 = ax1.step(E_center, fluence, where='mid', color=color_fluence, alpha=0.8, label='Fluence', linestyle='-')
ax1.tick_params(axis='y', labelcolor=color_fluence)

# Set energy axis to log scale (standard for radiation protection spectra)
ax1.set_xscale('log')
# Set fluence axis to log scale if it spans multiple orders of magnitude
ax1.set_yscale('log')

# Create a second y-axis sharing the same x-axis
ax2 = ax1.twinx()

# Plot ICRU factors and LUPIN ratio on the right y-axis (using log scale as well)
color_icru = 'tab:orange'
color_lupin = 'tab:green'

line2 = ax2.plot(E_center, icru_at_sim_energies, color=color_icru, label='ICRU Factor [pSv cm$^{2}$]', linestyle='--')
line3 = ax2.plot(E_center, lupin_ratio_at_sim_energies, color=color_lupin, label='LUPIN Ratio', linestyle='-.')

# Data from ELSE Nuclear
# Energy centrum from ELSE Nuclear (position 6)
energy_centrum_else = [1.27E-08, 1.60E-08, 2.01E-08, 2.53E-08, 3.18E-08, 4.01E-08, 5.05E-08, 6.35E-08, 8.00E-08, 1.01E-07, 1.27E-07, 1.60E-07, 2.01E-07, 2.53E-07, 3.18E-07, 4.01E-07, 5.05E-07, 6.35E-07, 8.00E-07, 1.01E-06, 1.27E-06, 1.60E-06, 2.01E-06, 2.53E-06, 3.18E-06, 4.01E-06, 5.05E-06, 6.35E-06, 8.00E-06, 1.01E-05, 1.27E-05, 1.60E-05, 2.01E-05, 2.53E-05, 3.18E-05, 4.01E-05, 5.05E-05, 6.35E-05, 8.00E-05, 1.01E-04, 0.000126729, 0.000159541, 0.000200852, 0.000252857, 0.000318328, 0.000400751, 0.000504513, 0.000635145, 0.000799601, 0.001006649, 0.001267295, 0.001595413, 0.002008524, 0.002528574, 0.00318328, 0.004007512, 0.00504513, 0.006351455, 0.00799605, 0.010066101, 0.012672387, 0.015954132, 0.020085242, 0.025285744, 0.031832798, 0.040075116, 0.050451301, 0.063514103, 0.079959942, 0.100661005, 0.126723868, 0.159541317, 0.200852417, 0.252857441, 0.318327977, 0.400751158, 0.504517465, 0.635146638, 0.799599418, 1.006610053, 1.267238675, 1.595413172, 2.008524175, 2.528574413, 3.183279766, 4.007511578, 5.045130083, 6.351454837, 7.996050278, 10.06654616, 12.67294776, 15.95413172, 20.08524175, 25.28574413, 31.83279766, 40.07511578, 50.45130083, 63.51454837, 79.96005715, 100.6604443, 126.7238675, 159.5413172, 200.8524175, 252.8574413, 318.3279766, 400.7511578, 504.5174645, 635.1510938, 799.6005715, 1006.604443]

# LUPIN response from ELSE Nuclear (nSv cm2)
lupin_response_else = [4.47E-03, 4.35E-03, 4.52E-03, 5.26E-03, 4.87E-03, 4.96E-03, 5.64E-03, 6.21E-03, 7.22E-03, 7.27E-03, 9.30E-03, 9.63E-03, 1.07E-02, 1.13E-02, 1.14E-02, 1.28E-02, 1.37E-02, 1.44E-02, 1.51E-02, 1.52E-02, 1.63E-02, 1.76E-02, 1.78E-02, 1.75E-02, 1.96E-02, 2.00E-02, 2.03E-02, 2.16E-02, 2.11E-02, 2.24E-02, 2.35E-02, 2.28E-02, 2.39E-02, 2.46E-02, 2.55E-02, 2.63E-02, 2.69E-02, 2.83E-02, 2.85E-02, 2.85E-02, 0.029651862, 0.029622746, 0.030899732, 0.03195568, 0.032030384, 0.03272621, 0.03396654, 0.034681216, 0.034887348, 0.037801036, 0.037366036, 0.037747154, 0.038408006, 0.040388474, 0.041148448, 0.042155386, 0.042649604, 0.04538761, 0.043724054, 0.047570846, 0.04880758, 0.050109158, 0.052954348, 0.055869022, 0.056676208, 0.05912114, 0.06600922, 0.06840926, 0.0742342, 0.08125046, 0.08929216, 0.09894162, 0.11192782, 0.12838184, 0.15109116, 0.17654736, 0.21444746, 0.2509486, 0.2930218, 0.33782564, 0.37499436, 0.41748168, 0.44993384, 0.46925132, 0.44420112, 0.42532676, 0.45460284, 0.43368978, 0.40160882, 0.34213736, 0.32150386, 0.29367488, 0.26843386, 0.25436654, 0.23164098, 0.21905846, 0.214513, 0.2149219, 0.2144086, 0.22201356, 0.2333804, 0.24294982, 0.26888104, 0.27311852, 0.29591426, 0.3162566, 0.34469516, 0.38353428, 0.43022718, 0.47279222]
lupin_response_else = [x*1000 for x in lupin_response_else] # convert to pSv cm2

# Convertion factors from ELSE Nuclear from fluence to dose H*(10) (pSv cm2)
conv_factors_else = [9.383712983, 9.772498935, 10.17734818, 10.59894685, 10.95365461, 11.32002342, 11.69865177, 12.08994208, 12.49431027, 12.90561297, 13.10199063, 13.30135319, 13.50046245, 13.52552301, 13.55063019, 13.5757842, 13.59606416, 13.4956944, 13.39606494, 13.29614025, 13.16194873, 13.02908828, 12.89567043, 12.66342745, 12.43536612, 12.21141004, 11.99064466, 11.7536177, 11.52128023, 11.29313945, 11.05576705, 10.82334912, 10.59663918, 10.41626881, 10.23896792, 10.06468339, 9.89335114, 9.72448949, 9.558502594, 9.395084952, 9.226041284, 9.060041858, 8.897117204, 8.742430844, 8.590433285, 8.441077042, 8.294687238, 8.159698022, 8.026906914, 7.898063469, 7.831071953, 7.764651337, 7.701366152, 7.775691366, 7.850734183, 7.926501926, 8.028251192, 8.787250894, 9.618019913, 10.5458115, 12.27884497, 14.29705728, 16.66211588, 20.39610481, 25.26409658, 32.38000703, 41.51735925, 53.78601201, 69.21314337, 88.58168463, 111.5170034, 139.356354, 170.5630585, 204.0007197, 241.9167899, 279.8964632, 323.3142374, 358.8473411, 388.0323782, 416.3218769, 424.4635418, 422.2049496, 419.915285, 415.3542978, 411.1722861, 407.9746844, 404.7521224, 401.8391596, 408.9851343, 441.3949549, 493.7937484, 554.3239803, 599.0393486, 549.2624609, 500.1117995, 446.2700239, 398.2983658, 357.0782328, 319.4044506, 284.229173, 258.8419155, 246.988125, 259.9459329, 260, 260, 260, 260, 260, 260, 260]

# Calculate the LUPIN ratio from ELSE Nuclear data to compare with your lupin_ratio_at_sim_energies
# Ratio = Absolute Response / Conversion Factor
lupin_ratio_else = [r / c for r, c in zip(lupin_response_else, conv_factors_else)]

# Plot ELSE Nuclear data on the right y-axis for comparison
# Using different styles and colors to distinguish them
line4 = ax2.plot(energy_centrum_else, conv_factors_else, color='purple', label='ELSE Conv. Factor [pSv cm$^{2}$]', linestyle=':')
line5 = ax2.plot(energy_centrum_else, lupin_ratio_else, color='cyan', label='ELSE LUPIN Ratio', linestyle=':')

ax2.set_ylabel('Conversion Factors & LUPIN Responses', color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax2.set_yscale('log')

# Combine legends from both axes into a single box
lines = line1 + line2 + line3 + line4 + line5
labels = [l.get_label() for l in lines]
# Place legend outside the plot or adjust location to avoid covering data
ax1.legend(lines, labels, loc='center left', bbox_to_anchor=(1.15, 0.5))

plt.title('Debug Plot: Fluence vs ICRU and LUPIN Response (My data vs ELSE)')
# Adjust layout to fit the external legend
fig.tight_layout()
plt.grid(True, which="both", linestyle=":", alpha=0.5)

plt.savefig('DEBUG_interpolatedcurves_withELSE.png', dpi=300, bbox_inches='tight')
plt.close()

# ==============================================================================
# DOSE COMPARISON PLOT
# ==============================================================================
# Create a new figure for comparing True Dose vs LUPIN Dose per bin
fig_dose, ax_dose = plt.subplots(figsize=(9, 6))

# Plot True Dose per bin using a step plot (ideal for binned data)
ax_dose.step(E_center, true_dose_per_bin, where='mid', color='tab:blue',
             alpha=0.8, label='True Dose H*(10)', linestyle='-')

# Plot LUPIN estimated Dose per bin
ax_dose.step(E_center, lupin_dose_per_bin, where='mid', color='tab:red',
             alpha=0.8, label='LUPIN Estimated Dose', linestyle='--')

# Set axes labels
ax_dose.set_xlabel('Energy $E_{center}$ [MeV]')
ax_dose.set_ylabel('Ambient Dose Equivalent per bin [pSv]')

# Set axes to log scale (standard for dosimetric distributions over energy)
ax_dose.set_xscale('log')
ax_dose.set_yscale('log')

# Add legend, title, and grid for readability
ax_dose.legend(loc='upper left')
plt.title('Analytical Dose Comparison: True H*(10) vs LUPIN Estimate')
plt.grid(True, which="both", linestyle=":", alpha=0.5)

# Adjust layout to prevent clipping
fig_dose.tight_layout()

# Save the figure to file and close the plot
plt.savefig('DEBUG_dose_comparison.png', dpi=300)
plt.close(fig_dose)

# ==============================================================================
# OUTPUT RESULTS
# ==============================================================================
print("-" * 50)
print(f"Total True H*(10) Dose:  {total_true_dose:.4e} pSv")
print(f"Total LUPIN H*(10) Dose: {total_lupin_dose:.4e} pSv")
print(f"LUPIN Correction Factor: {lupin_correction_factor:.4f}")
print("-" * 50)

# ==============================================================================
# PLOTTING CONFIGURATION (Toggle mask on/off)
# ==============================================================================
use_lupin_mask = False  # Set to False to disable masking and show full extrapolation

if use_lupin_mask:
    # Restrict arrays strictly to the original LUPIN energy bounds
    lupin_plot_mask = (E_center >= lupin_energies_MeV.min()) & (E_center <= lupin_energies_MeV.max())
    plot_E = E_center[lupin_plot_mask]
    plot_ratio = lupin_ratio_at_sim_energies[lupin_plot_mask]
else:
    # Use full simulation spectrum arrays (including flat extrapolations)
    plot_E = E_center
    plot_ratio = lupin_ratio_at_sim_energies

# --- Plot 1: LUPIN Response Ratio vs Energy (Log-Log) ---
fig, ax = plt.subplots(figsize=(10, 5))

# Arrays adapt dynamically based on the use_lupin_mask flag
ax.plot(plot_E, plot_ratio, color='darkviolet', marker='.', linestyle='-', linewidth=1.5, label='LUPIN Response Ratio')

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Energy (MeV)', fontsize=11)
ax.set_ylabel('Response Ratio (Response / ICRU Factor)', fontsize=11)
ax.grid(True, which="both", linestyle="--", alpha=0.5)
ax.axhline(1.0, color='gray', linestyle=':', alpha=0.7, label='Ideal Response (1.0)')

# Enforce view limits only if the mask is enabled
if use_lupin_mask:
    ax.set_xlim(lupin_energies_MeV.min(), lupin_energies_MeV.max())

ax.legend(loc='upper right')
plt.title('LUPIN Detector Response Ratio vs Incident Neutron Energy', fontsize=13, pad=10)
plt.tight_layout()
plt.savefig('lupin_response_ratio_only.png', dpi=300)
plt.close()

# --- Plot 2: Vertical Subplots ---
fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Top Subplot: Full Neutron Fluence from FLUKA (always full range)
ax_top.plot(E_center, fluence, color='blue', marker='.', linestyle='-', linewidth=1.5, label='Neutron Fluence')
ax_top.set_yscale('log')
ax_top.set_ylabel('Fluence (particles/cm$^2$)', fontsize=11)
ax_top.grid(True, which="both", linestyle="--", alpha=0.5)
ax_top.set_title('Neutron Spectrum Fluence vs LUPIN Response Curve Comparison', fontsize=13, pad=10)
ax_top.legend(loc='upper right')

# Bottom Subplot: Interpolated LUPIN Response Ratio (dynamic range)
ax_bot.plot(plot_E, plot_ratio, color='darkviolet', marker='.', linestyle='-', linewidth=1.5, label='LUPIN Response Ratio')
ax_bot.set_xscale('log')
ax_bot.set_yscale('log')
ax_bot.set_xlabel('Energy (MeV)', fontsize=11)
ax_bot.set_ylabel('Response Ratio', fontsize=11)
ax_bot.axhline(1.0, color='gray', linestyle=':', alpha=0.7)
ax_bot.grid(True, which="both", linestyle="--", alpha=0.5)
ax_bot.legend(loc='upper right')

# Align the shared X-axis limits to the LUPIN definition range if masked
if use_lupin_mask:
    ax_bot.set_xlim(lupin_energies_MeV.min(), lupin_energies_MeV.max())

plt.tight_layout()
plt.savefig('neutron_fluence_and_lupin_ratio_stacked.png', dpi=300)
plt.close()
