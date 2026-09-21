#ifndef DetectorConstruction_h
#  define DetectorConstruction_h 1

#  include "G4VUserDetectorConstruction.hh"
#  include "globals.hh"

class G4VPhysicalVolume;
class G4LogicalVolume;

class DetectorConstruction : public G4VUserDetectorConstruction
{
  public:
    DetectorConstruction();
    ~DetectorConstruction() override = default;

    G4VPhysicalVolume* Construct() override;

    G4LogicalVolume* GetLayerLogicalVolume(G4int layer) const;
    G4int GetNumberOfLayers() const;
    G4double GetSourceZ() const;

  private:
    G4LogicalVolume* fLayerLogicalVolume = nullptr;
    G4VPhysicalVolume* fWorldPhysicalVolume = nullptr;
};

#endif  // DetectorConstruction_h 1
