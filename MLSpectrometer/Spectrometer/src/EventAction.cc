#include "EventAction.hh"
#include "DetectorConstruction.hh"
#include "RunAction.hh"
#include "SimulationConfig.hh"

#include "G4Event.hh"
#include "G4SystemOfUnits.hh"

#include <algorithm>
#include <cmath>

EventAction::EventAction(const DetectorConstruction *detector,
                         RunAction *runAction)
    : fDetector(detector), fRunAction(runAction) {
  fLayerEdep.resize(SimulationConfig::NumberOfLayers, 0.0);
  fPrimarySpectrum.resize(SimulationConfig::NumberOfEnergyBins, 0.0);
}

void EventAction::BeginOfEventAction(const G4Event *) {
  std::fill(fLayerEdep.begin(), fLayerEdep.end(), 0.0);
  ResetPrimarySpectrum();
  fNumberOfPrimaryGammas = 0;
  fTotalPrimaryEnergy = 0.0;
  fGeneratedMean = 0.0;
  fGeneratedSigma = 0.0;
}

void EventAction::EndOfEventAction(const G4Event *event) {
  if (fRunAction != nullptr) {
    fRunAction->FillEvent(event, *this);
  }
}

void EventAction::AddEnergyDeposit(G4int layer, G4double energy) {
  if (layer >= 0 && layer < static_cast<G4int>(fLayerEdep.size())) {
    fLayerEdep[layer] += energy;
  }
}

void EventAction::AddPrimaryGamma(G4double energy) {
  ++fNumberOfPrimaryGammas;
  fTotalPrimaryEnergy += energy;

  const G4double binWidth =
      (SimulationConfig::EnergyMax - SimulationConfig::EnergyMin) /
      SimulationConfig::NumberOfEnergyBins;

  G4int bin = static_cast<G4int>(
      std::floor((energy - SimulationConfig::EnergyMin) / binWidth));

  bin = std::max(0, std::min(bin, SimulationConfig::NumberOfEnergyBins - 1));
  fPrimarySpectrum[bin] += 1.0;
}

void EventAction::SetGeneratedSpectrumParameters(G4double mean,
                                                 G4double sigma) {
  fGeneratedMean = mean;
  fGeneratedSigma = sigma;
}

void EventAction::ResetPrimarySpectrum() {
  std::fill(fPrimarySpectrum.begin(), fPrimarySpectrum.end(), 0.0);
}

const std::vector<G4double> &EventAction::GetLayerEdep() const {
  return fLayerEdep;
}

const std::vector<G4double> &EventAction::GetPrimarySpectrum() const {
  return fPrimarySpectrum;
}

G4int EventAction::GetNumberOfPrimaryGammas() const {
  return fNumberOfPrimaryGammas;
}

G4double EventAction::GetTotalPrimaryEnergy() const {
  return fTotalPrimaryEnergy;
}

G4double EventAction::GetGeneratedMean() const { return fGeneratedMean; }

G4double EventAction::GetGeneratedSigma() const { return fGeneratedSigma; }
