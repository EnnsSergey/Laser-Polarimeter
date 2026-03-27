#ifndef DETECTOR_HH
#define DETECTOR_HH
#include "G4VSensitiveDetector.hh"
#include "G4AnalysisManager.hh"
#include "G4RunManager.hh"
#include "event.hh"
#include "G4EventManager.hh"
#include "G4Event.hh"
class SensitiveDetector : public G4VSensitiveDetector
{
  public:
    SensitiveDetector(G4String);
    ~SensitiveDetector();

  private:
    virtual G4bool ProcessHits(G4Step*, G4TouchableHistory*);
};

#endif
