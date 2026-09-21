#include "RunAction.hh"
#include "DetectorConstruction.hh"
#include "EventAction.hh"
#include "SimulationConfig.hh"

#include "G4AnalysisManager.hh"
#include "G4Event.hh"
#include "G4Run.hh"
#include "G4SystemOfUnits.hh"

RunAction::RunAction(const DetectorConstruction *detector)
    : fDetector(detector) {
  auto *analysisManager = G4AnalysisManager::Instance();
  analysisManager->SetDefaultFileType("root");
  analysisManager->SetVerboseLevel(1);
  analysisManager->SetNtupleMerging(true);

  analysisManager->CreateNtuple("LayerSignals",
                                "Gamma layer spectrometer data");
  analysisManager->CreateNtupleIColumn("event");
  analysisManager->CreateNtupleIColumn("n_primary_gammas");
  analysisManager->CreateNtupleDColumn("total_primary_energy_MeV");
  analysisManager->CreateNtupleDColumn("generated_mean_MeV");
  analysisManager->CreateNtupleDColumn("generated_sigma_MeV");

  for (G4int i = 0; i < SimulationConfig::NumberOfLayers; ++i) {
    analysisManager->CreateNtupleDColumn("layer_" + std::to_string(i) + "_MeV");
  }

  for (G4int i = 0; i < SimulationConfig::NumberOfEnergyBins; ++i) {
    analysisManager->CreateNtupleDColumn("gamma_bin_" + std::to_string(i));
  }

  analysisManager->FinishNtuple();
}

RunAction::~RunAction() = default;

void RunAction::BeginOfRunAction(const G4Run *) {
  auto *analysisManager = G4AnalysisManager::Instance();
  analysisManager->OpenFile("layer_signals.root");
}

void RunAction::EndOfRunAction(const G4Run *) {
  auto *analysisManager = G4AnalysisManager::Instance();
  analysisManager->Write();
  analysisManager->CloseFile();
}

void RunAction::FillEvent(const G4Event *event,
                          const EventAction &eventAction) {
  auto *analysisManager = G4AnalysisManager::Instance();

  analysisManager->FillNtupleIColumn(0, event->GetEventID());
  analysisManager->FillNtupleIColumn(1, eventAction.GetNumberOfPrimaryGammas());
  analysisManager->FillNtupleDColumn(2,
                                     eventAction.GetTotalPrimaryEnergy() / MeV);
  analysisManager->FillNtupleDColumn(3, eventAction.GetGeneratedMean() / MeV);
  analysisManager->FillNtupleDColumn(4, eventAction.GetGeneratedSigma() / MeV);

  const auto &layerEdep = eventAction.GetLayerEdep();
  for (G4int i = 0; i < SimulationConfig::NumberOfLayers; ++i) {
    analysisManager->FillNtupleDColumn(5 + i, layerEdep[i] / MeV);
  }

  const auto &spectrum = eventAction.GetPrimarySpectrum();
  const G4int firstSpectrumColumn = 5 + SimulationConfig::NumberOfLayers;
  for (G4int i = 0; i < SimulationConfig::NumberOfEnergyBins; ++i) {
    analysisManager->FillNtupleDColumn(firstSpectrumColumn + i, spectrum[i]);
  }

  analysisManager->AddNtupleRow();
}
