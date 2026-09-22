#ifndef EVENT_ACTION_HH
#define EVENT_ACTION_HH

#include "G4UserEventAction.hh"
#include "globals.hh"

#include <vector>

class DetectorConstruction;
class RunAction;

class EventAction : public G4UserEventAction {
public:
  EventAction(const DetectorConstruction *detector, RunAction *runAction);
  ~EventAction() override = default;

  void BeginOfEventAction(const G4Event *event) override;
  void EndOfEventAction(const G4Event *event) override;

  void AddEnergyDeposit(G4int layer, G4double energy);
  void AddPrimaryGamma(G4double energy);
  void SetGeneratedSpectrumParameters(G4double mean, G4double sigma);

  void ResetPrimarySpectrum();

  const std::vector<G4double> &GetLayerEdep() const;
  const std::vector<G4double> &GetPrimarySpectrum() const;
  G4int GetNumberOfPrimaryGammas() const;
  G4double GetTotalPrimaryEnergy() const;
  G4double GetGeneratedMean() const;
  G4double GetGeneratedSigma() const;

  void ResetPrimaryTruth();

private:
  const DetectorConstruction *fDetector = nullptr;
  RunAction *fRunAction = nullptr;

  std::vector<G4double> fLayerEdep;
  std::vector<G4double> fPrimarySpectrum;

  G4int fNumberOfPrimaryGammas = 0;
  G4double fTotalPrimaryEnergy = 0.0;
  G4double fGeneratedMean = 0.0;
  G4double fGeneratedSigma = 0.0;
};

#endif
