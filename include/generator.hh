#ifndef GENERATOR_HH
#define GENERATOR_HH

#include "G4VUserPrimaryGeneratorAction.hh"
#include "G4ParticleGun.hh"
#include "G4SystemOfUnits.hh"
#include "G4ParticleTable.hh"
#include "compton.hh"
#include "G4EventManager.hh"
#include "params.hh"


class PrimaryGenerator : public G4VUserPrimaryGeneratorAction
{
	public:
		PrimaryGenerator(const Params& param, int thr_num);
		~PrimaryGenerator();
		virtual void GeneratePrimaries(G4Event*);
		Compton compt;

	private:
		G4ParticleGun* fParticleGun; 
		Params fParams;
};


#endif
