#ifndef ACTION_HH
#define ACTION_HH

#include "G4VUserActionInitialization.hh"
#include "generator.hh"
#include "run.hh"
#include "event.hh"
#include "params.hh"

class ActionInitialization : public G4VUserActionInitialization
{
	public:
		ActionInitialization(const Params& params, int thr_num);
		~ActionInitialization();
		virtual void Build() const;
	private:

		Params fParams;
		int fThrNum;
};


#endif
