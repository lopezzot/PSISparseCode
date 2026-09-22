#ifndef SPECTRUM_GENERATOR_HH
#define SPECTRUM_GENERATOR_HH

#include "globals.hh"

#include <vector>

class SpectrumGenerator {
public:
  SpectrumGenerator();
  ~SpectrumGenerator() = default;

  std::vector<G4double> GenerateGammaEnergies(G4int numberOfGammas);

  G4double GetLastMean() const;
  G4double GetLastSigma() const;

private:
  // Gaussian spectrum
  std::vector<G4double> GenerateGaussianSpectrum(G4int numberOfGammas);

  G4double SampleGaussianEnergy(G4double mean, G4double sigma) const;

  // Accelerator-like spectrum
  std::vector<G4double> GenerateAcceleratorSpectrum(G4int numberOfGammas);

  G4double EvaluateAcceleratorSpectrum(
      G4double energy, G4double continuumPower, G4double continuumAmplitude,
      G4double continuumTurnOn, G4double continuumCutoff,
      const std::vector<G4double> &peakEnergies,
      const std::vector<G4double> &peakSigmas,
      const std::vector<G4double> &peakAmplitudes) const;

  G4double fLastMean = 0.0;
  G4double fLastSigma = 0.0;
};

#endif
