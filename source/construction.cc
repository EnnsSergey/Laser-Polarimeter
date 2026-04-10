#include "construction.hh"
#include <cmath>
#include "G4AssemblyVolume.hh"

DetectorConstruction::DetectorConstruction()
{}

DetectorConstruction::~DetectorConstruction()
{}

G4VPhysicalVolume* DetectorConstruction::Construct()
{

	struct GeometryConfig {
		//фланец
		G4double flange_diam = 40*mm;
		G4double flange_thick = 1.5*mm;

		//зеркало
		G4double mirrorDiam = 100*mm;
		std::vector<G4double> mirrorThick = {4*mm, 1*mm, 17*mm, 1*mm};
		
		G4double fl_dist=8.835*m; // расстояние до фланца
		G4double d_fl_mirr = 230*mm;  //расстояние между зеркалом и фланцем - 23 см
		G4double mr_dist = fl_dist - d_fl_mirr; // расстояние до зеркала

		//поворот зеркала
		G4double mirror_angle = 45.0*deg;
		G4RotationMatrix* rotation;

		//конвертер
		G4double conv_dist = 29.9*m;
		G4double conv_sizeX = 161.4*mm;
		G4double conv_sizeY = 50.35*mm;
		G4double conv_sizeZ = 12*mm;

		//детектор
		G4double det_sizeX = 161.4*mm;
		G4double det_sizeY = 50.35*mm;
		G4double det_sizeZ = 3 * mm;

		G4int padRows = 20;
		G4int padCols = 32;

		G4double det_dist = conv_dist+conv_sizeZ; 
		//расстояние между зеркалом и фланцем - 23 см

		//расстояние между детектором и конвертером
		G4double conv_det_dist = 0*mm;

		G4double GetZsize (void)const{
			return det_sizeZ + conv_sizeZ + conv_det_dist; 
		}
		GeometryConfig()
		{
			rotation = new G4RotationMatrix();
			rotation->rotateY(mirror_angle);
		}
		~GeometryConfig()
		{
		}
	};

	GeometryConfig gc;

	G4double worldSizeXY = 1.5 * gc.mirrorDiam;
	G4double worldSizeZ = 1.5 * gc.det_dist;

	//вакуум

	G4double vacuumSizeXY = worldSizeXY;
	G4double vacuumSizeZ = gc.fl_dist;

	// материалы:
	G4NistManager* nist = G4NistManager::Instance();

	G4Material* convMat = nist->FindOrBuildMaterial("G4_Pb");

	G4Material* worldMat = nist -> FindOrBuildMaterial("G4_AIR");

	G4Material* vacuum = nist->FindOrBuildMaterial("G4_Galactic");

	G4Material* detMat = nist->FindOrBuildMaterial("G4_Ar");

	G4Material* flMat = nist -> FindOrBuildMaterial("G4_Fe");

	std::vector<G4Material*> mirrMat =
	{
		nist -> FindOrBuildMaterial("G4_Cu"),
		nist -> FindOrBuildMaterial("G4_Fe"),
		nist -> FindOrBuildMaterial("G4_WATER"),
		nist -> FindOrBuildMaterial("G4_Fe")

	};

	//солиды:
	G4Box* solidConv = new G4Box("solidConv", 0.5*gc.conv_sizeX, 0.5*gc.conv_sizeY, 0.5*gc.conv_sizeZ);

	G4Box* solidWorld = new G4Box("solidWorld", 0.5*worldSizeXY, 0.5*worldSizeXY, worldSizeZ);

	G4Box* solidDet = new G4Box("solidDet", 0.5*gc.det_sizeX, 0.5*gc.det_sizeY, 0.5*gc.det_sizeZ);

	G4Tubs* solidFlange = new G4Tubs("solidFlange", 0.0, 0.5*gc.flange_diam, 0.5*gc.flange_thick, 0.0*deg, 360.0*deg);

	G4Box* solidVacuum = new G4Box("solidVacuum",0.5*vacuumSizeXY, 0.5*vacuumSizeXY, 0.5*vacuumSizeZ);





	//логические:
	G4LogicalVolume* logicConv = new G4LogicalVolume(solidConv, convMat, "logicConv");

	G4LogicalVolume* logicWorld = new G4LogicalVolume(solidWorld, worldMat, "logicWorld");

	logicDet = new G4LogicalVolume(solidDet, detMat, "logicDet");

	G4LogicalVolume* logicFlange = new G4LogicalVolume(solidFlange, flMat, "logicFlange");

	G4LogicalVolume* logicVacuum = new G4LogicalVolume(solidVacuum, vacuum, "logicVacuum");


	//цвета:

	G4VisAttributes* worldColour = new G4VisAttributes();
	worldColour -> SetVisibility(false);
	logicWorld -> SetVisAttributes(worldColour);
	
	G4VisAttributes* detColour = new G4VisAttributes(G4Colour(0.5, 0.2, 1.0));
	detColour -> SetVisibility(true);
	logicDet -> SetVisAttributes(detColour);

	G4VisAttributes* flangeColour = new G4VisAttributes(G4Colour(1., 1., 1.));
	flangeColour -> SetVisibility(true);
	logicFlange -> SetVisAttributes(flangeColour);

	G4VisAttributes* vacuumColour = new G4VisAttributes(G4Colour(0.5, 0.2, 1.0));
	vacuumColour -> SetVisibility(false);
	logicVacuum -> SetVisAttributes(vacuumColour);

	//физические:

	G4VPhysicalVolume *physWorld = new G4PVPlacement(0, G4ThreeVector(0,0,0), logicWorld, "physWorld", 0, false, 0, true);

	G4VPhysicalVolume *physConv = new G4PVPlacement(0, G4ThreeVector(0,0,gc.conv_dist+0.5*gc.conv_sizeZ), logicConv, "physConv", logicWorld, false, 0, true);

	G4VPhysicalVolume* physDet = new G4PVPlacement(0, G4ThreeVector(0, 0, gc.det_dist+0.5*gc.det_sizeZ), logicDet, "physDet", logicWorld, false, 0, true);

	G4VPhysicalVolume* physFlange = new G4PVPlacement(0, G4ThreeVector(0,0,gc.fl_dist+0.5*gc.flange_thick), logicFlange, "physFlange", logicWorld, false, 0, true);

	G4VPhysicalVolume* physVacuum = new G4PVPlacement(0, G4ThreeVector(0,0,0.5*vacuumSizeZ), logicVacuum, "physVacuum", logicWorld, false, 0, true);




	//ЗЕРКАЛО

	G4double mirrorLayerZ = gc.mr_dist;

	std::vector<G4Colour> mirrCol = 
	{
		G4Colour(1., 0., 0),
		G4Colour(1, 1., 1),
		G4Colour(0, 0., 1),
		G4Colour(1, 1., 1),
	};
	G4AssemblyVolume* mirror = new G4AssemblyVolume();	
	
	G4double totalThick = 0;
	for (auto t : gc.mirrorThick) totalThick += t; //расчёт толщины зеркала
	G4double zPos = -totalThick/2; //локальная координа z начинается с -половины всей толщины, чтобы центр был в нуле

	G4double vacuumCenter = 0.5 * vacuumSizeZ;
	G4double mirrorRelZ = gc.mr_dist - vacuumCenter; // координата зеркала относительно вакуума
	for (int i = 0; i<4; i++)
	{	
		G4Tubs* solidMirr = new G4Tubs("solidMirr" + std::to_string(i), 0.0, 0.5 * gc.mirrorDiam, 0.5 * gc.mirrorThick[i], 0.0*deg, 360*deg);
		G4LogicalVolume* logicMirror = new G4LogicalVolume(solidMirr, mirrMat[i], "logicMirr" + std::to_string(i));

		G4VisAttributes* mirrColour = new G4VisAttributes(mirrCol[i]);
		mirrColour -> SetVisibility(true);
		logicMirror -> SetVisAttributes(mirrColour);

		G4ThreeVector pos(0,0,zPos + 0.5*gc.mirrorThick[i]);	
		mirror -> AddPlacedVolume(logicMirror, pos, nullptr);
		zPos += gc.mirrorThick[i];	
	}
	G4ThreeVector mirrorPos = G4ThreeVector(0,0,mirrorRelZ);
	mirror -> MakeImprint(logicVacuum, mirrorPos,  gc.rotation); // размещение и поворот
	return physWorld;
}



void DetectorConstruction::ConstructSDandField()
{
	SensitiveDetector* sensDet = new SensitiveDetector("SensitiveDetector");
	logicDet->SetSensitiveDetector(sensDet);
}
