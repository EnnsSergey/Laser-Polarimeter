#ifndef  CONSTRUCTION_HH
#define CONSTRUCTION_HH

#include "G4SystemOfUnits.hh"
#include "G4VUserDetectorConstruction.hh"
#include "G4VPhysicalVolume.hh"
#include "G4Box.hh"
#include "G4PVPlacement.hh"
#include "G4NistManager.hh"
#include "G4LogicalVolume.hh"
#include "G4VisAttributes.hh"
#include "detector.hh"
#include "G4Tubs.hh"
#include "params.hh"
#include <vector>


class DetectorConstruction : public G4VUserDetectorConstruction
{
	public:
		DetectorConstruction(const Params& params);
		~DetectorConstruction();

		virtual G4VPhysicalVolume* Construct();
	private:
		G4LogicalVolume* logicDet;
		virtual void ConstructSDandField();
		Params fParams;

};


#endif  
