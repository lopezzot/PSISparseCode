# Spectrometer
A simple Geant4 simulation needed to understand if a longitudinally segmented calorimeter can work as a spectrometer for pulsed gamma fields with machine learning reconstruction.

## Build, compile and execute
1. source Geant4 env
   ```sh
   source /relative_path_to/geant4-install/bin/geant4.sh
   ```
2. build directory, cmake and make
   ```sh
   mkdir build; cd build
   cmake -DGeant4_DIR=/absolute_path_to/geant4-install/lib/Geant4/ relative_path_to/Spectrometer
   make
   ```
3. execute with visualization
   ```sh
   ./Spectrometer
   ```
4. or, execute with macro card
   ```sh
   ./Spectrometer run.mac
   ```
