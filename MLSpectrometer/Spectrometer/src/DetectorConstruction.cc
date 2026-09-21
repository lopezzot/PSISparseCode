#include "G4Box.hh"
#include "G4LogicalVolume.hh"
#include "G4Material.hh"
#include "G4NistManager.hh"
#include "G4PVPlacement.hh"
#include "G4SystemOfUnits.hh"
#include "G4VisAttributes.hh"

#include "DetectorConstruction.hh"
#include "SimulationConfig.hh"

#include "G4Box.hh"
#include "G4LogicalVolume.hh"
#include "G4Material.hh"
#include "G4NistManager.hh"
#include "G4PVPlacement.hh"
#include "G4SystemOfUnits.hh"
#include "G4ThreeVector.hh"
#include "G4VisAttributes.hh"
#include "G4Colour.hh"

DetectorConstruction::DetectorConstruction() = default;

G4VPhysicalVolume* DetectorConstruction::Construct()
{
    auto* nist = G4NistManager::Instance();
    auto* air = nist->FindOrBuildMaterial("G4_AIR");
    auto* plastic = nist->FindOrBuildMaterial("G4_PLASTIC_SC_VINYLTOLUENE");

    const G4double detectorThickness =
        SimulationConfig::NumberOfLayers * SimulationConfig::LayerThickness +
        (SimulationConfig::NumberOfLayers - 1) * SimulationConfig::LayerGap;

    const G4double worldXY = 160.0 * mm;
    const G4double worldZ = 400.0 * mm;

    auto* worldSolid = new G4Box(
        "WorldSolid", worldXY / 2.0, worldXY / 2.0, worldZ / 2.0);
    auto* worldLogical = new G4LogicalVolume(worldSolid, air, "WorldLogical");

    fWorldPhysicalVolume = new G4PVPlacement(
        nullptr,
        G4ThreeVector(),
        worldLogical,
        "WorldPhysical",
        nullptr,
        false,
        0,
        true);

    auto* layerSolid = new G4Box(
        "LayerSolid",
        SimulationConfig::LayerSizeXY / 2.0,
        SimulationConfig::LayerSizeXY / 2.0,
        SimulationConfig::LayerThickness / 2.0);

    fLayerLogicalVolume = new G4LogicalVolume(
        layerSolid, plastic, "ScintillatorLayerLogical");

    const G4double detectorFrontZ = 0.0 * mm;
    const G4double firstLayerZ =
        detectorFrontZ + SimulationConfig::LayerThickness / 2.0;

    for (G4int i = 0; i < SimulationConfig::NumberOfLayers; ++i) {
        const G4double z = firstLayerZ +
            i * (SimulationConfig::LayerThickness + SimulationConfig::LayerGap);

        new G4PVPlacement(
            nullptr,
            G4ThreeVector(0.0, 0.0, z),
            fLayerLogicalVolume,
            "ScintillatorLayer",
            worldLogical,
            false,
            i,
            true);
    }

    auto* worldVis = new G4VisAttributes();
    worldVis->SetForceWireframe(true);
    worldLogical->SetVisAttributes(worldVis);

    auto* layerVis = new G4VisAttributes(G4Colour(0.2, 0.7, 1.0, 0.3));
    layerVis->SetForceSolid(true);
    fLayerLogicalVolume->SetVisAttributes(layerVis);

    return fWorldPhysicalVolume;
}

G4LogicalVolume* DetectorConstruction::GetLayerLogicalVolume(G4int) const
{
    return fLayerLogicalVolume;
}

G4int DetectorConstruction::GetNumberOfLayers() const
{
    return SimulationConfig::NumberOfLayers;
}

G4double DetectorConstruction::GetSourceZ() const
{
    return -50.0 * mm;
}
