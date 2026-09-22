#ifndef ActionInitialization_h
#define ActionInitialization_h 1

#include "G4VUserActionInitialization.hh"

#include "DetectorConstruction.hh"
#include "G4VUserDetectorConstruction.hh"

class ActionInitialization : public G4VUserActionInitialization {
public:
  explicit ActionInitialization(const DetectorConstruction *detector);
  ~ActionInitialization() override = default;

  void BuildForMaster() const override;
  void Build() const override;

private:
  const DetectorConstruction *fDetector = nullptr;
};

#endif // ActionInitialization_h 1
