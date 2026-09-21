#ifndef ActionInitialization_h
#  define ActionInitialization_h 1

#  include "G4VUserActionInitialization.hh"

# include "G4VUserDetectorConstruction.hh"
#include "DetectorConstruction.hh"

class ActionInitialization : public G4VUserActionInitialization
{
  public:
    explicit ActionInitialization(const DetectorConstruction* detector);
    ~ActionInitialization() override = default;

    void BuildForMaster() const override;
    void Build() const override;

private:
    const DetectorConstruction* fDetector = nullptr;
};

#endif  // ActionInitialization_h 1
