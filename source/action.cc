#include "action.hh"

ActionInitialization::ActionInitialization(const Params& params, int thr_num) : fParams(params), fThrNum(thr_num)
{}

ActionInitialization::~ActionInitialization()
{}

void ActionInitialization::Build() const
{
	PrimaryGenerator* generator = new PrimaryGenerator(fParams);
	SetUserAction(generator);

	RunAction* runAct = new RunAction(fThrNum, fParams);
	SetUserAction(runAct);

	EventAction* eventAct = new EventAction(runAct);
	SetUserAction(eventAct);
}
