#ifndef SIMULATION_CONFIG_HH
#define SIMULATION_CONFIG_HH

#include "G4SystemOfUnits.hh"
#include "globals.hh"

namespace SimulationConfig {
constexpr G4int NumberOfLayers = 30;
constexpr G4double LayerThickness = 5.0 * mm;
constexpr G4double LayerSizeXY = 100.0 * mm;
constexpr G4double LayerGap = 0.0 * mm;

constexpr G4int NumberOfEnergyBins = 100;
constexpr G4double EnergyMin = 0.1 * MeV;
constexpr G4double EnergyMax = 10.0 * MeV;

// First training configuration: one Gaussian spectrum per shot.
constexpr G4double GaussianMeanMin = 1.0 * MeV;
constexpr G4double GaussianMeanMax = 9.0 * MeV;
constexpr G4double GaussianSigmaMin = 0.1 * MeV;
constexpr G4double GaussianSigmaMax = 0.8 * MeV;

// Keep the first dataset statistically simple: fixed number of photons per
// shot.
constexpr G4int NumberOfPrimaryGammas = 100;
} // namespace SimulationConfig

#endif
