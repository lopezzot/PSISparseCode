#ifndef RUN_ACTION_HH
#define RUN_ACTION_HH

#include "G4UserRunAction.hh"
#include "globals.hh"

class DetectorConstruction;
class EventAction;
class G4Event;
class G4Run;

class RunAction : public G4UserRunAction {
public:
  explicit RunAction(const DetectorConstruction *detector);
  ~RunAction() override;

  void BeginOfRunAction(const G4Run *run) override;
  void EndOfRunAction(const G4Run *run) override;

  void FillEvent(const G4Event *event, const EventAction &eventAction);

private:
  const DetectorConstruction *fDetector = nullptr;
};

#endif
