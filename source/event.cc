#include "event.hh"

EventAction::EventAction(RunAction* runAction)
	: fRunAction(runAction)
{}

EventAction::~EventAction()
{}

void EventAction::BeginOfEventAction(const G4Event* event)
{
	// Очищаем ReadOut в начале каждого события
	readOut.Clear();
	
	
}

void EventAction::EndOfEventAction(const G4Event* event)
{
	G4int nEvent = event -> GetEventID();

	// Заполняем гистограмму в RunAction
	for(int i = 0; i < ReadOut::YSIZE; i++) {
		for(int j = 0; j < ReadOut::XSIZE; j++) {
			if(abs(readOut.charge[i][j]) > 0) {  // Порог можно настроить
				if (nEvent % 2 == 0){ fRunAction->histogram_r[i][j] += 1; }
				else { fRunAction->histogram_l[i][j] += 1; }
			}
		}
	}
}
