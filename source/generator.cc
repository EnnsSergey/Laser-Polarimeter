#include "generator.hh"
#include "G4SystemOfUnits.hh"
#include <cmath>
#include "Randomize.hh"
PrimaryGenerator::PrimaryGenerator(const Params& params, int thr_num) : fParams(params), compt(1000+thr_num, 4730.0)
{

	fParticleGun = new G4ParticleGun(1);

	G4ParticleTable* particleTable = G4ParticleTable::GetParticleTable();
	G4String particleName = "gamma";
	G4ParticleDefinition* particle = particleTable->FindParticle(particleName);

	G4ThreeVector pos(G4RandGauss::shoot(0, fParams.sigma_x), G4RandGauss::shoot(0, fParams.sigma_y), 0);	
	fParticleGun->SetParticlePosition(pos);

	//fParticleGun->SetParticleMomentum(800*MeV);
	fParticleGun->SetParticleDefinition(particle);


}

PrimaryGenerator::~PrimaryGenerator()
{
	delete fParticleGun;
}

void PrimaryGenerator::GeneratePrimaries(G4Event* event)
{	
	
	std::cout<<"P "<<fParams.P<<" "<<"Q "<<fParams.Q<<" "<<"beta "<<fParams.beta<<std::endl;

	G4int nEvent = event -> GetEventID();
	bool pol =(nEvent % 2 == 0);
	std::cout<<"POL "<< pol<<std::endl;
	std::tuple<double, double>  angles = compt.Neumann(fParams.P, fParams.Q, fParams.beta, pol);
	double theta_x = std::get<0>(angles);
	double theta_y = std::get<1>(angles);

	double disp_x = G4RandGauss::shoot(0, fParams.d_theta_x);
	double disp_y = G4RandGauss::shoot(0, fParams.d_theta_y);

	double theta_e = sqrt(disp_x*disp_x + disp_y*disp_y);        // угол электрона

	double theta = sqrt(theta_x*theta_x + theta_y*theta_y);
	// проекции полного угла отклонения фотона
	
	double beta = sqrt(1 - 1/(compt.gamma * compt.gamma));
	
	double bracket1 = 1 - (theta_e*theta_e)/2;
	double bracket2 = 1 - (theta * theta) / 2;
	double bracket3 = 2 - ((theta_x + disp_x)*(theta_x+disp_x) + (theta_y + disp_y)*(theta_y + disp_y))/2;
	double PhotonEnergy = (compt.o) * (1 + beta * bracket1) / (1 - beta * bracket2 + compt.o * bracket3/compt.get_energy());

	fParticleGun -> SetParticleMomentum(PhotonEnergy * MeV);

	G4ThreeVector mom(theta_x + disp_x, theta_y + disp_y, 1); 
	
	fParticleGun->SetParticleMomentumDirection(mom);
	//fParticleGun->SetParticleMomentumDirection(G4ThreeVector(0,0,1));

	fParticleGun->GeneratePrimaryVertex(event);
}
