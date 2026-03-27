#include "compton.hh"

extern std::mt19937 Gen;
std::vector<double> ElectronBeam::BoxMuller()
{

	std::vector<double> un(2);
	double s;
	while(true){
		std::uniform_real_distribution<> dist(-1, 1);
		un[0] = dist(Gen);
		un[1] = dist(Gen);
		s = un[0]*un[0] + un[1]*un[1];

		if (s>0 && s<=1) break;}
	std::vector<double> Z(2);
	Z[0]= un[0] * sqrt(-2*std::log(s)/s);
	Z[1]= un[1] * sqrt(-2*std::log(s)/s);

	return Z;


}
double Compton::Generator(double theta_x, double theta_y, double P, double Q0, double beta, bool pol) //генератор рассеяния
{		

	double V, Q;
	if (pol) 
	{ 
		V = sqrt(1.0-Q0*Q0);
		Q = Q0;
	}
	else 
	{
		V = -sqrt(1.0-Q0 * Q0);
		Q = -Q0;
	}
	
	double theta = sqrt(theta_x*theta_x+theta_y*theta_y); 
	double phi = std::atan2(theta_y,theta_x);
	double eta = g*theta;

	double eta2 = pow(eta, 2.0);
	
	double t = 1.0 + eta2 + kappa;

	double A = pow(1.0 + kappa, 2.0) / (1.0 + 0.5 * pow(kappa, 2.0) / (1.0 + kappa));

	double sigma = A / pow(t, 2.0) * (1.0 + 0.5 * (pow(kappa, 2.0)) / (t * (1.0 + eta2)) -
		+ 2.0 * pow(eta / (1.0 + eta2), 2.0) * (1.0 - Q * cos(2.0 * (phi - beta))) +
		+ P * V * eta * kappa / (t * (1.0 + eta2)) * sin(phi));
	return sigma;

}
std::vector<double> Compton::Neumann(double P, double Q, double beta, bool pol) // метод Неймана
{
	
	std::vector<double> angles(2); // вектор, состоящий из углов theta_x, theta_y
	while(true){
		std::uniform_real_distribution<> distrib_angle(-4/g,4/g); // равномерное распределение в пределах нескольких характерных углов 
		angles[0]=distrib_angle(Gen);
		angles[1]=distrib_angle(Gen);
		std::uniform_real_distribution<> distrib_sigma(0.0, 2+kappa*kappa+(3*sqrt(3)*kappa/8)); // равномерное распр от нуля до макс
		double sigm = distrib_sigma(Gen);
		double sigma = Generator(angles[0],angles[1],P,Q,beta,pol);
		if (sigma > sigm) 
		{	
			break;
		}
	}

	// если точка лежит под графиком распределения, то углы соотв распределению
	return angles;
}


