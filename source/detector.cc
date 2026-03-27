#include "detector.hh"

SensitiveDetector::SensitiveDetector(G4String name) : G4VSensitiveDetector(name)
{}

SensitiveDetector::~SensitiveDetector()
{}

G4bool SensitiveDetector::ProcessHits(G4Step *step, G4TouchableHistory* ROhist)
{
	G4Track* track = step -> GetTrack();

	//track -> SetTrackStatus(fStopAndKill);

	G4StepPoint* preStepPoint = step->GetPreStepPoint();
	G4StepPoint* postStepPoint = step->GetPostStepPoint();

	G4ThreeVector particlePos = preStepPoint->GetPosition();

	auto eventManager = G4EventManager::GetEventManager();
	auto eventAction = static_cast<EventAction*>(eventManager->GetUserEventAction());

	if(eventAction) {
		// Рассчитываем заряд (энергия/энергия ионизации)
		G4double energyDeposit = step->GetTotalEnergyDeposit();
		G4double ionizationEnergy = 30*eV;  // Для аргона
		float charge = energyDeposit / ionizationEnergy;

		// Определяем знак заряда
		G4String particleName = track->GetParticleDefinition()->GetParticleName();
		if(particleName == "e-") {
			charge = -charge;  // Электроны дают отрицательный заряд
		}

		// Добавляем заряд в ReadOut
		eventAction->readOut.AddCharge(particlePos.x(), particlePos.y(), charge);
	}
	const G4VTouchable* touchable = step -> GetPreStepPoint() -> GetTouchable();
	return true;
}
