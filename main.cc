#include <iostream>
#include "G4RunManager.hh"
#include "G4UImanager.hh"
#include "G4VisManager.hh"
#include "G4UIExecutive.hh"
#include "G4VisExecutive.hh"
#include "construction.hh"
#include "physics.hh"
#include "action.hh"
#include "params.hh"
#include "run.hh"
#include <random>
#include <ctime>
std::mt19937 Gen;


int main(int argc, char** argv)
{

	Params params;
	

	int thr_num = 0;

	if (argc > 2)
	{
		thr_num = std::atoi(argv[2]);
	}
	for (int i = 3; i < argc; ++i) 
	{
		if (std::string(argv[i]) == "--P" && i+1 < argc)
			params.P = std::atof(argv[++i]);
		else if (std::string(argv[i]) == "--Q" && i+1 < argc)
			params.Q = std::atof(argv[++i]);
		else if (std::string(argv[i]) == "--beta" && i+1 < argc)
			params.beta = std::atof(argv[++i]); 
		else if (std::string(argv[i]) == "--sx" && i+1 < argc)
			params.d_theta_x = pow(10,-6) * std::atof(argv[++i]);
		else if (std::string(argv[i]) == "--sy" && i+1 < argc)
			params.d_theta_y = pow(10,-6) * std::atof(argv[++i]);
	}

	G4RunManager* runManager = new G4RunManager; 

	Gen.seed(thr_num + std::time(0));
	runManager -> SetUserInitialization(new DetectorConstruction());
	runManager -> SetUserInitialization(new PhysicsList());
	runManager -> SetUserInitialization(new ActionInitialization(params, thr_num));
	runManager -> Initialize();    
	

	G4UIExecutive* ui = nullptr;


	G4UImanager *UImanager = G4UImanager::GetUIpointer();

	if (argc==1)
	{
		ui = new G4UIExecutive(argc, argv);
	}

	G4VisManager* visManager = new G4VisExecutive();
	visManager -> Initialize();

	if(ui)
	{
		UImanager->ApplyCommand("/control/execute vis.mac");
		ui->SessionStart();
	}
	else
	{
		G4String comm = "/control/execute ";
		G4String macFile = argv[1];

		UImanager->ApplyCommand(comm+macFile);

	}


	return 0;

}
