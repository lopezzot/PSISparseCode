#ifndef SIMULATION_CONFIG_HH
#define SIMULATION_CONFIG_HH

#include "G4SystemOfUnits.hh"
#include "globals.hh"

// --------------------------------------------------
// Spectrum model selection
// --------------------------------------------------

// Available models:
//   SPECTRUM_GAUSSIAN
//   SPECTRUM_ACCELERATOR

#define SPECTRUM_ACCELERATOR

namespace SimulationConfig {

constexpr G4int NumberOfLayers = 90;
constexpr G4double LayerThickness = 5.0 * mm;
constexpr G4double LayerSizeXY = 100.0 * mm;
constexpr G4double LayerGap = 0.0 * mm;

// --------------------------------------------------
// Energy spectrum
// --------------------------------------------------

constexpr G4int NumberOfEnergyBins = 100;
constexpr G4double EnergyMin = 0.1 * MeV;
constexpr G4double EnergyMax = 100.0 * MeV;

// --------------------------------------------------
// Gaussian spectrum parameters
// --------------------------------------------------

constexpr G4double GaussianMeanMin = 10.0 * MeV;
constexpr G4double GaussianMeanMax = 90.0 * MeV;

constexpr G4double GaussianSigmaMin = 1.0 * MeV;
constexpr G4double GaussianSigmaMax = 10.0 * MeV;

// --------------------------------------------------
// Accelerator-like spectrum parameters
// --------------------------------------------------

//
// The parameters are randomized event by event within
// these ranges.

// Number of spectral peaks generated per event.
constexpr G4int AcceleratorNumberOfPeaksMin = 1;
constexpr G4int AcceleratorNumberOfPeaksMax = 1;

// Peak energy range.
constexpr G4double AcceleratorPeakEnergyMin = 1.0 * MeV;
constexpr G4double AcceleratorPeakEnergyMax = 80.0 * MeV;

// Peak width.
constexpr G4double AcceleratorPeakSigmaMin = 0.2 * MeV;
constexpr G4double AcceleratorPeakSigmaMax = 3.0 * MeV;

// Relative peak amplitude.
constexpr G4double AcceleratorPeakAmplitudeMin = 0.2;
constexpr G4double AcceleratorPeakAmplitudeMax = 2.0;

// Continuum power-law parameters.
constexpr G4double AcceleratorContinuumPowerMin = 0.5;
constexpr G4double AcceleratorContinuumPowerMax = 1.5;

// Continuum normalization.
constexpr G4double AcceleratorContinuumAmplitudeMin = 0.5;
constexpr G4double AcceleratorContinuumAmplitudeMax = 1.0;

// Low-energy smoothing scale.
constexpr G4double AcceleratorContinuumTurnOnMin = 2.0 * MeV;
constexpr G4double AcceleratorContinuumTurnOnMax = 8.0 * MeV;

// High-energy exponential cutoff.
constexpr G4double AcceleratorContinuumCutoffMin = 50.0 * MeV;
constexpr G4double AcceleratorContinuumCutoffMax = 100.0 * MeV;

// --------------------------------------------------
// Primary statistics
// --------------------------------------------------

constexpr G4int NumberOfPrimaryGammas = 10000;

} // namespace SimulationConfig

#endif
