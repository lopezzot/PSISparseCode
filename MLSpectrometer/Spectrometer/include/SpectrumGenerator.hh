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
  G4double SampleGaussianEnergy(G4double mean, G4double sigma) const;

  G4double fLastMean = 0.0;
  G4double fLastSigma = 0.0;
};

#endif
