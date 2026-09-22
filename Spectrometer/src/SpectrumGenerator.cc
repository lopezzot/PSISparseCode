#include "SpectrumGenerator.hh"
#include "SimulationConfig.hh"

#include "G4SystemOfUnits.hh"
#include "Randomize.hh"

#include <algorithm>
#include <cmath>
#include <vector>

SpectrumGenerator::SpectrumGenerator() = default;

std::vector<G4double>
SpectrumGenerator::GenerateGammaEnergies(G4int numberOfGammas) {

#ifdef SPECTRUM_GAUSSIAN

  return GenerateGaussianSpectrum(numberOfGammas);

#elif defined(SPECTRUM_ACCELERATOR)

  return GenerateAcceleratorSpectrum(numberOfGammas);

#else

#error "No spectrum model selected"

#endif
}

// --------------------------------------------------
// Gaussian spectrum
// --------------------------------------------------

std::vector<G4double>
SpectrumGenerator::GenerateGaussianSpectrum(G4int numberOfGammas) {

  fLastMean = G4UniformRand() * (SimulationConfig::GaussianMeanMax -
                                 SimulationConfig::GaussianMeanMin) +
              SimulationConfig::GaussianMeanMin;

  fLastSigma = G4UniformRand() * (SimulationConfig::GaussianSigmaMax -
                                  SimulationConfig::GaussianSigmaMin) +
               SimulationConfig::GaussianSigmaMin;

  std::vector<G4double> energies;
  energies.reserve(numberOfGammas);

  for (G4int i = 0; i < numberOfGammas; ++i) {

    energies.push_back(SampleGaussianEnergy(fLastMean, fLastSigma));
  }

  return energies;
}

G4double SpectrumGenerator::SampleGaussianEnergy(G4double mean,
                                                 G4double sigma) const {

  // Rejection sampling enforces the physical simulation energy range.
  G4double energy = 0.0;

  do {
    energy = mean + sigma * G4RandGauss::shoot();

  } while (energy < SimulationConfig::EnergyMin ||
           energy > SimulationConfig::EnergyMax);

  return energy;
}

// --------------------------------------------------
// Accelerator-like spectrum
// --------------------------------------------------

std::vector<G4double>
SpectrumGenerator::GenerateAcceleratorSpectrum(G4int numberOfGammas) {

  // Randomize continuum parameters for this event.
  const G4double continuumPower =
      G4UniformRand() * (SimulationConfig::AcceleratorContinuumPowerMax -
                         SimulationConfig::AcceleratorContinuumPowerMin) +
      SimulationConfig::AcceleratorContinuumPowerMin;

  const G4double continuumAmplitude =
      G4UniformRand() * (SimulationConfig::AcceleratorContinuumAmplitudeMax -
                         SimulationConfig::AcceleratorContinuumAmplitudeMin) +
      SimulationConfig::AcceleratorContinuumAmplitudeMin;

  // Randomize continuum low-energy smoothing scale.
  const G4double continuumTurnOn =
      G4UniformRand() * (SimulationConfig::AcceleratorContinuumTurnOnMax -
                         SimulationConfig::AcceleratorContinuumTurnOnMin) +
      SimulationConfig::AcceleratorContinuumTurnOnMin;

  // Randomize continuum high-energy cutoff.
  const G4double continuumCutoff =
      G4UniformRand() * (SimulationConfig::AcceleratorContinuumCutoffMax -
                         SimulationConfig::AcceleratorContinuumCutoffMin) +
      SimulationConfig::AcceleratorContinuumCutoffMin;

  // Randomize the number of peaks.
  const G4int numberOfPeaks =
      SimulationConfig::AcceleratorNumberOfPeaksMin +
      static_cast<G4int>(G4UniformRand() *
                         (SimulationConfig::AcceleratorNumberOfPeaksMax -
                          SimulationConfig::AcceleratorNumberOfPeaksMin + 1));

  std::vector<G4double> peakEnergies;
  std::vector<G4double> peakSigmas;
  std::vector<G4double> peakAmplitudes;

  peakEnergies.reserve(numberOfPeaks);
  peakSigmas.reserve(numberOfPeaks);
  peakAmplitudes.reserve(numberOfPeaks);

  for (G4int i = 0; i < numberOfPeaks; ++i) {

    const G4double peakEnergy =
        G4UniformRand() * (SimulationConfig::AcceleratorPeakEnergyMax -
                           SimulationConfig::AcceleratorPeakEnergyMin) +
        SimulationConfig::AcceleratorPeakEnergyMin;

    const G4double peakSigma =
        G4UniformRand() * (SimulationConfig::AcceleratorPeakSigmaMax -
                           SimulationConfig::AcceleratorPeakSigmaMin) +
        SimulationConfig::AcceleratorPeakSigmaMin;

    const G4double peakAmplitude =
        G4UniformRand() * (SimulationConfig::AcceleratorPeakAmplitudeMax -
                           SimulationConfig::AcceleratorPeakAmplitudeMin) +
        SimulationConfig::AcceleratorPeakAmplitudeMin;

    peakEnergies.push_back(peakEnergy);
    peakSigmas.push_back(peakSigma);
    peakAmplitudes.push_back(peakAmplitude);
  }

  // Find the maximum spectrum value for rejection sampling.
  const G4int numberOfGridPoints = 1000;

  G4double maximumSpectrum = 0.0;

  for (G4int i = 0; i < numberOfGridPoints; ++i) {

    const G4double energy =
        SimulationConfig::EnergyMin +
        (SimulationConfig::EnergyMax - SimulationConfig::EnergyMin) *
            (static_cast<G4double>(i) / (numberOfGridPoints - 1));

    const G4double value = EvaluateAcceleratorSpectrum(
        energy, continuumPower, continuumAmplitude, continuumTurnOn,
        continuumCutoff, peakEnergies, peakSigmas, peakAmplitudes);

    maximumSpectrum = std::max(maximumSpectrum, value);
  }

  std::vector<G4double> energies;
  energies.reserve(numberOfGammas);

  // Rejection sampling generates gamma energies according to
  // the accelerator-like spectrum.
  while (static_cast<G4int>(energies.size()) < numberOfGammas) {

    const G4double energy = G4UniformRand() * (SimulationConfig::EnergyMax -
                                               SimulationConfig::EnergyMin) +
                            SimulationConfig::EnergyMin;

    const G4double spectrumValue = EvaluateAcceleratorSpectrum(
        energy, continuumPower, continuumAmplitude, continuumTurnOn,
        continuumCutoff, peakEnergies, peakSigmas, peakAmplitudes);

    const G4double randomValue = G4UniformRand() * maximumSpectrum;

    if (randomValue <= spectrumValue) {
      energies.push_back(energy);
    }
  }

  // These values are retained only for compatibility with the
  // existing ROOT output.
  //
  // They are not used to describe the accelerator-like spectrum.
  G4double mean = 0.0;

  for (const auto energy : energies) {
    mean += energy;
  }

  mean /= energies.size();

  G4double variance = 0.0;

  for (const auto energy : energies) {
    const G4double difference = energy - mean;
    variance += difference * difference;
  }

  variance /= energies.size();

  fLastMean = mean;
  fLastSigma = std::sqrt(variance);

  return energies;
}

G4double SpectrumGenerator::EvaluateAcceleratorSpectrum(
    G4double energy, G4double continuumPower, G4double continuumAmplitude,
    G4double continuumTurnOn, G4double continuumCutoff,
    const std::vector<G4double> &peakEnergies,
    const std::vector<G4double> &peakSigmas,
    const std::vector<G4double> &peakAmplitudes) const {

  // Avoid numerical problems at very low energy.
  const G4double safeEnergy = std::max(energy, 1e-6 * MeV);

  // Smooth power-law continuum.
  const G4double continuum =
      continuumAmplitude *
      std::pow(1.0 + safeEnergy / continuumTurnOn, -continuumPower) *
      std::exp(-safeEnergy / continuumCutoff);

  G4double spectrum = continuum;

  // Add Gaussian spectral structures.
  for (std::size_t i = 0; i < peakEnergies.size(); ++i) {

    const G4double difference = energy - peakEnergies[i];

    const G4double gaussian =
        peakAmplitudes[i] * std::exp(-0.5 * difference * difference /
                                     (peakSigmas[i] * peakSigmas[i]));

    spectrum += gaussian;
  }

  return spectrum;
}

// --------------------------------------------------
// Existing interface
// --------------------------------------------------

G4double SpectrumGenerator::GetLastMean() const { return fLastMean; }

G4double SpectrumGenerator::GetLastSigma() const { return fLastSigma; }
