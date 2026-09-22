// Includers from project files
//
#include "ActionInitialization.hh"
#include "DetectorConstruction.hh"

// Includers from Geant4
//
#include "G4PhysListFactory.hh"
#include "G4RunManagerFactory.hh"
#include "G4UIExecutive.hh"
#include "G4UImanager.hh"
#include "G4VisExecutive.hh"

int main(int argc, char **argv) {
  // Set user interface
  //
  G4UIExecutive *ui = nullptr;
  if (argc == 1) {
    ui = new G4UIExecutive(argc, argv);
  }
  // Initialize visualization
  //
  G4VisManager *visManager = new G4VisExecutive;
  visManager->Initialize();
  // Get the pointer to the User Interface manager
  //
  G4UImanager *UImanager = G4UImanager::GetUIpointer();

  // Construct the default run manager
  //
  auto *runManager =
      G4RunManagerFactory::CreateRunManager(G4RunManagerType::Default);

  // Physics list
  G4PhysListFactory PLFactory;
  G4VModularPhysicsList *PL = PLFactory.GetReferencePhysList("FTFP_BERT");
  runManager->SetUserInitialization(PL);

  // Detector constructioin and action initialization
  //
  DetectorConstruction *detConstruction = new DetectorConstruction();
  runManager->SetUserInitialization(detConstruction);
  runManager->SetUserInitialization(new ActionInitialization(detConstruction));

  // Process macro or start UI session
  //
  if (!ui) {
    // batch mode
    G4String command = "/control/execute ";
    G4String fileName = argv[1];
    UImanager->ApplyCommand(command + fileName);
  } else {
    // interactive mode
    UImanager->ApplyCommand("/control/execute init_vis.mac");
    ui->SessionStart();
    delete ui;
  }

  delete visManager;
  delete runManager;
}
