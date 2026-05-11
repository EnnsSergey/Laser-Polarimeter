#ifndef RUN_HH
#define RUN_HH

#include "G4UserRunAction.hh"
#include "G4AnalysisManager.hh"
#include "G4Run.hh"
#include <array>
#include "readOut.hh"
#include <fstream>
#include <iostream>
#include "params.hh"
#include "event.hh"
#include <vector>
class RunAction : public G4UserRunAction
{
	public:
		RunAction(int thr_num, Params params);
		~RunAction();

		virtual void BeginOfRunAction(const G4Run*);
		virtual void EndOfRunAction(const G4Run*);
		std::array<std::array<G4int, ReadOut::XSIZE>, ReadOut::YSIZE> histogram_l;
		std::array<std::array<G4int, ReadOut::XSIZE>, ReadOut::YSIZE> histogram_r;
		std::vector<int> spectrum;
		int thr_num;	
		Params fParams;

};

#endif
