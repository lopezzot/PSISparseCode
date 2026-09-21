#include "ActionInitialization.hh"
#include "DetectorConstruction.hh"
#include "EventAction.hh"
#include "PrimaryGeneratorAction.hh"
#include "RunAction.hh"
#include "SteppingAction.hh"

ActionInitialization::ActionInitialization(const DetectorConstruction *detector)
    : fDetector(detector) {}

void ActionInitialization::BuildForMaster() const {
  SetUserAction(new RunAction(fDetector));
}

void ActionInitialization::Build() const {
  auto *runAction = new RunAction(fDetector);
  SetUserAction(runAction);

  auto *eventAction = new EventAction(fDetector, runAction);
  SetUserAction(eventAction);

  SetUserAction(new PrimaryGeneratorAction(fDetector, eventAction));
  SetUserAction(new SteppingAction(fDetector, eventAction));
}
