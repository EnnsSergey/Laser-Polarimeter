#ifndef EVENT_HH
#define EVENT_HH

#include "G4UserEventAction.hh"
#include "readOut.hh"
#include "run.hh"
#include "G4EventManager.hh"
#include "G4RunManager.hh"

class RunAction;

class EventAction : public G4UserEventAction
{
	public:
		EventAction(RunAction* runAction);
		~EventAction();

		virtual void BeginOfEventAction(const G4Event*);
		virtual void EndOfEventAction(const G4Event*);

		ReadOut readOut;  

	private:
		RunAction* fRunAction;
};

#endif
