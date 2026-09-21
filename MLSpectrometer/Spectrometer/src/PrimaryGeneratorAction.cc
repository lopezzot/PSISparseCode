#include "PrimaryGeneratorAction.hh"
#include "DetectorConstruction.hh"
#include "EventAction.hh"
#include "SimulationConfig.hh"
#include "SpectrumGenerator.hh"

#include "G4Event.hh"
#include "G4Gamma.hh"
#include "G4ParticleGun.hh"
#include "G4SystemOfUnits.hh"
#include "G4ThreeVector.hh"

PrimaryGeneratorAction::PrimaryGeneratorAction(const DetectorConstruction* detector,
                                               EventAction* eventAction)
    : fDetector(detector),
      fEventAction(eventAction),
      fParticleGun(new G4ParticleGun(1)),
      fSpectrumGenerator(std::make_unique<SpectrumGenerator>())
{
    fParticleGun->SetParticleDefinition(G4Gamma::Definition());
    fParticleGun->SetParticleMomentumDirection(G4ThreeVector(0.0, 0.0, 1.0));
}

PrimaryGeneratorAction::~PrimaryGeneratorAction()
{
    delete fParticleGun;
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* event)
{
    const auto energies = fSpectrumGenerator->GenerateGammaEnergies(
        SimulationConfig::NumberOfPrimaryGammas);

    fEventAction->ResetPrimarySpectrum();
    fEventAction->SetGeneratedSpectrumParameters(
        fSpectrumGenerator->GetLastMean(),
        fSpectrumGenerator->GetLastSigma());

    for (const auto energy : energies) {
        fParticleGun->SetParticleEnergy(energy);
        fParticleGun->SetParticlePosition(
            G4ThreeVector(0.0, 0.0, fDetector->GetSourceZ()));
        fParticleGun->GeneratePrimaryVertex(event);

        fEventAction->AddPrimaryGamma(energy);
    }
}

