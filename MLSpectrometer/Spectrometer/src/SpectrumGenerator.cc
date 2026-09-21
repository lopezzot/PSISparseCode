#include "SpectrumGenerator.hh"
#include "SimulationConfig.hh"

#include "Randomize.hh"
#include "G4SystemOfUnits.hh"

#include <cmath>

SpectrumGenerator::SpectrumGenerator() = default;

std::vector<G4double> SpectrumGenerator::GenerateGammaEnergies(G4int numberOfGammas)
{
    fLastMean = G4UniformRand() *
        (SimulationConfig::GaussianMeanMax - SimulationConfig::GaussianMeanMin) +
        SimulationConfig::GaussianMeanMin;

    fLastSigma = G4UniformRand() *
        (SimulationConfig::GaussianSigmaMax - SimulationConfig::GaussianSigmaMin) +
        SimulationConfig::GaussianSigmaMin;

    std::vector<G4double> energies;
    energies.reserve(numberOfGammas);

    for (G4int i = 0; i < numberOfGammas; ++i) {
        energies.push_back(SampleGaussianEnergy(fLastMean, fLastSigma));
    }

    return energies;
}

G4double SpectrumGenerator::SampleGaussianEnergy(G4double mean, G4double sigma) const
{
    // Rejection sampling enforces the physical simulation energy range.
    G4double energy = 0.0;
    do {
        energy = mean + sigma * G4RandGauss::shoot();
    } while (energy < SimulationConfig::EnergyMin ||
             energy > SimulationConfig::EnergyMax);

    return energy;
}

G4double SpectrumGenerator::GetLastMean() const
{
    return fLastMean;
}

G4double SpectrumGenerator::GetLastSigma() const
{
    return fLastSigma;
}
