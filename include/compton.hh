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


class Compton
{
	public:
		static double P;
		static double Q;
		static double beta;
		static int n;
		static constexpr double pi = M_PI;



		double me = 0.5109989461e6;
		double o = 2.3526413364;
		double g = 9245.67;
		double kappa = 4.0*g*o/me;
		

		double Generator(double theta_x, double theta_y, double P, double Q, double beta, bool pol);
		std::vector<double> Neumann(double P, double Q, double beta, bool pol);
		
};
class ElectronBeam
{
	public:
		
		double g = 9245.67;
		std::vector<double> BoxMuller();

};
#endif // COMPTON_H

