#ifndef COMPTON_H
#define COMPTON_H

#include <fstream>
#include <iostream>
#include <vector>
#include <random>
#include <chrono>
#include <fstream>
#include <cmath>
#include <cstdlib>

#include <tuple>

class Compton
{
	public:
		static double P;
		static double Q;
		static double beta;
		static int n;
		static constexpr double pi = M_PI;
		
		static constexpr double me = 0.5109989461;
		static constexpr double o = 2.3526413364e-6; //MeV
		double Energy;
		double gamma;
		double kappa;
		
		std::mt19937 gen;


    Compton(unsigned seed, double E=4730.0);


    std::tuple<double, double> Neumann(double P, double Q, double beta, bool pol);

    double get_kappa(void) const {return kappa;}

    double get_gamma(void) const {return gamma;}

    double get_energy(void) const {return Energy;}

};

#endif // COMPTON_H
