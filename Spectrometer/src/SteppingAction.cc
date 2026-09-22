#include "SteppingAction.hh"
#include "DetectorConstruction.hh"
#include "EventAction.hh"

#include "G4Step.hh"
#include "G4StepPoint.hh"
#include "G4VPhysicalVolume.hh"

SteppingAction::SteppingAction(const DetectorConstruction *detector,
                               EventAction *eventAction)
    : fDetector(detector), fEventAction(eventAction) {}

void SteppingAction::UserSteppingAction(const G4Step *step) {
  const auto *prePoint = step->GetPreStepPoint();
  const auto *volume = prePoint->GetPhysicalVolume();

  if (volume == nullptr) {
    return;
  }

  const auto *logical = volume->GetLogicalVolume();
  if (logical != fDetector->GetLayerLogicalVolume(0)) {
    return;
  }

  const G4int layer = volume->GetCopyNo();
  const G4double edep = step->GetTotalEnergyDeposit();

  if (edep > 0.0) {
    fEventAction->AddEnergyDeposit(layer, edep);
  }
}
