#include "generator.hh"
#include "G4SystemOfUnits.hh"
#include <cmath>
#include "Randomize.hh"
PrimaryGenerator::PrimaryGenerator(const Params& params) : fParams(params), compt(4730.0, 42)
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
	G4int nEvent = event -> GetEventID();
	std::tuple<double, double>  angles = compt.Neumann(fParams.P, fParams.Q, fParams.beta, (nEvent % 2 == 0));
	double theta_x = std::get<0>(angles);
	double theta_y = std::get<1>(angles);
	double disp_x = G4RandGauss::shoot(0, fParams.d_theta_x);
	double disp_y = G4RandGauss::shoot(0, fParams.d_theta_y);
//	std::cout<<"GAMMA "<<compt.get_gamma()<< std::endl;

//	std::cout<<"УГЛЫ "<<theta_x<<" "<< theta_y<< std::endl;

        //std::cout<<"DISP "<<fParams.d_theta_x<<" "<<fParams.d_theta_y<<std::endl;
	double beta = sqrt(1 - 1/(compt.gamma * compt.gamma));
	
	double theta_e = disp_x*disp_x + disp_y*disp_y;        // угол электрона
	double theta_gamma = theta_x*theta_x + theta_y*theta_y; // угол рассеянного фотона

	double bracket1 = theta_e/2 - 1;
	double bracket2 = 1 - theta_gamma / 2;
	double bracket3 = 2 - ((disp_x + theta_x)*(disp_x + theta_x) + (disp_y + theta_y)*(disp_y + theta_y));
	double PhotonEnergy = (compt.o) * (1 - beta * bracket1) / (1 - beta * bracket2 + compt.o * bracket3/compt.get_energy());

	//std::cout<<"ЭНЕРГИЯ ФОТОНА до "<< compt.o<< std::endl;
	//std::cout<<"ЭНЕРГИЯ ФОТОНА после "<< PhotonEnergy<< std::endl;
	fParticleGun -> SetParticleMomentum(PhotonEnergy * MeV);

	G4ThreeVector mom(theta_x + disp_x, theta_y + disp_y, 1); //второй порядок по углуу отброшен
	
	fParticleGun->SetParticleMomentumDirection(mom);
	//fParticleGun->SetParticleMomentumDirection(G4ThreeVector(0,0,1));

	fParticleGun->GeneratePrimaryVertex(event);
}
