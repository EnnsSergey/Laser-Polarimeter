#ifndef PARAMS_HH
#define PARAMS_HH

#include "G4SystemOfUnits.hh"
struct Params
{
	
	// параметры Стокса по умолчанию
	double P = 0.0;
	double Q = 0.0;
	double beta = 0.;

	// угловой разброс в пучке
	double d_theta_x = 0; //0.0006;
	double d_theta_y = 0;// 0.0001;

	// разброс по координатам
	G4double sigma_x = 0; // 4.3 * mm;
	G4double sigma_y = 0; //0.38 * mm;

	G4double conv_thick = 12*mm; // толщина конвертера по умолчанию
};

#endif
