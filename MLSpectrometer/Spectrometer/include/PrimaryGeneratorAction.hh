#ifndef PRIMARY_GENERATOR_ACTION_HH
#define PRIMARY_GENERATOR_ACTION_HH

#include "G4VUserPrimaryGeneratorAction.hh"
#include "globals.hh"

#include <memory>

class DetectorConstruction;
class EventAction;
class G4Event;
class G4ParticleGun;
class SpectrumGenerator;

class PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction {
public:
    PrimaryGeneratorAction(const DetectorConstruction* detector,
                           EventAction* eventAction);
    ~PrimaryGeneratorAction() override;

    void GeneratePrimaries(G4Event* event) override;

private:
    const DetectorConstruction* fDetector = nullptr;
    EventAction* fEventAction = nullptr;
    G4ParticleGun* fParticleGun = nullptr;
    std::unique_ptr<SpectrumGenerator> fSpectrumGenerator;
};

#endif
