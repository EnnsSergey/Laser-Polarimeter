#include "generator.hh"
#include "G4SystemOfUnits.hh"
#include <cmath>

PrimaryGenerator::PrimaryGenerator(const Params& params) : fParams(params)
{

	fParticleGun = new G4ParticleGun(1);

	G4ParticleTable* particleTable = G4ParticleTable::GetParticleTable();
	G4String particleName = "gamma";
	G4ParticleDefinition* particle = particleTable->FindParticle(particleName);

	std::vector<double> disp = beam.BoxMuller();
	
	G4ThreeVector pos(fParams.sigma_x * disp[0], fParams.sigma_y * disp[1], 0);	
//	G4ThreeVector pos (0,0,0);		
	fParticleGun->SetParticlePosition(pos);

	fParticleGun->SetParticleMomentum(800*MeV);
	fParticleGun->SetParticleDefinition(particle);


}

PrimaryGenerator::~PrimaryGenerator()
{
	delete fParticleGun;
}

void PrimaryGenerator::GeneratePrimaries(G4Event* event)
{	
	G4int nEvent = event -> GetEventID();
	std::vector<double> angles = compt.Neumann(fParams.P, fParams.Q,  fParams.beta, (nEvent % 2 == 0));
	std::vector<double> elAngles = beam.BoxMuller();
	G4ThreeVector mom(angles[0] + fParams.d_theta_x * elAngles[0], angles[1] + fParams.d_theta_y * elAngles[1], 1);
	fParticleGun->SetParticleMomentumDirection(mom);


	fParticleGun->GeneratePrimaryVertex(event);
}
