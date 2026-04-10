#include "compton.hh"


inline double branchless_atan2(double y, double x) {
    double abs_y = std::abs(y);
    double abs_x = std::abs(x);
    bool swap = abs_y > abs_x;
    double a = swap ? abs_x / abs_y : abs_y / abs_x;
    
    double s = a * a;
    double r = ((-0.0464964749 * s + 0.15931422) * s - 0.327622764) * s * a + a;
    
    if (swap) r = 1.57079632679 - r;
    if (x < 0) r = 3.14159265359 - r;
    if (y < 0) r = -r;
    return r;
}
/*
std::tuple<double, double> Compton::Neumann(double P, double Q, double beta, bool pol) // метод Неймана
{
	unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
	std::mt19937 gen(seed);

	double theta_x;
	double theta_y;
	while(true){
		std::uniform_real_distribution<> distrib_angle(-4/gamma,4/gamma); // равномерное распределение в пределах нескольких характерных углов 
		theta_x=distrib_angle(gen);
		theta_y=distrib_angle(gen);
		std::uniform_real_distribution<> distrib_sigma(0.0, 2+kappa*kappa+(3*sqrt(3)*kappa/8)); // равномерное распр от нуля до макс
		double sigm = distrib_sigma(gen);


		double V = sqrt(1.0-Q);
		double* pV = &V;
		double* pQ = &Q;
		if (pol){
			*pV = V;
			*pQ = Q;
		}
		else {
			*pV = -V;
			*pQ = -Q;

		}

		double theta = sqrt(theta_x*theta_x+theta_y*theta_y); 
		double phi = std::atan2(theta_y,theta_x);
		double eta = gamma*theta;

		double eta2 = pow(eta, 2.0);
		double t = 1.0+eta2+kappa;
		double A = 1/pow(t, 2.0);
		double sigma = A*(2.0 + (pow(kappa,2.0))/(t*(1.0+eta2))-(4.0*eta2/pow((1+eta2),2.0))*(1.0-Q*cos(2.0*(phi-beta)))+2*P*V*eta*sin(phi)*kappa/((1.0+eta2)*t));//сечение рассеяния
		if (sigma > sigm) break;} // если точка лежит под графиком распределения, то углы соотв распределению
	return {theta_x, theta_y};
	}*/

Compton::Compton(double E, unsigned seed)
	: Energy(E)
	, gamma(Energy/me)
	, kappa(4.0*gamma*o/me)
	  , gen(seed)
{
}





// Метод Неймана с аналитическим сэмплированием радиальной части.
// Огибающая: p(η) ∝ η/(1+η²+κ)², CDF(η²) = η²/(1+η²+κ)
// Обратная CDF: η² = (1+κ)·v/(1-v)
// Rejection только по скобке сечения (азимутальная модуляция от поляризации).


std::tuple<double, double> Compton::Neumann(double P, double Q, double beta, bool pol)
{
	double V, Qeff;
	if (pol) {
		V = sqrt(1.0 - Q*Q);
		Qeff = Q;
	} else {
		V = -sqrt(1.0 - Q*Q);
		Qeff = -Q;
	}







		// Максимальный η для генерации (η=10 покрывает 98.8% распределения)
	constexpr double ETA_MAX = 10.0;
	const double s_max = ETA_MAX * ETA_MAX;
	const double v_max = s_max / (1.0 + s_max + kappa);

	// Верхняя граница скобки сечения для rejection
	// bracket = 1 + 0.5κ²/(t(1+η²)) - 2(η/(1+η²))²(1 - Qeff·cos(2(φ-β))) + PV·ηκ/(t(1+η²))·sin(φ)
	// Максимум по φ ≤ 1 + 0.5κ²/(1+κ)² + 0.5|Q| + |PV|κ/(2(2+κ)) ≈ 1.06
	constexpr double B_MAX = 1.1; // с запасом

	std::uniform_real_distribution<> dist_v(0.0, v_max);
	std::uniform_real_distribution<> dist_phi(0.0, 2.0 * M_PI);
	std::uniform_real_distribution<> dist_u(0.0, B_MAX);

	while (true) {
		// η из аналитической огибающей (inverse CDF)
		double v = dist_v(gen);
		double eta2 = (1.0 + kappa) * v / (1.0 - v);
		double eta = sqrt(eta2);

		// φ равномерно
		double phi = dist_phi(gen);

		// Скобка сечения (без 1/t² — оно уже учтено в огибающей)
		double t = 1.0 + eta2 + kappa;
		double q = 1.0 + eta2;
		double eta_over_q = eta / q;
		double bracket = 1.0
			+ 0.5 * kappa*kappa / (t * q)
			- 2.0 * eta_over_q * eta_over_q * (1.0 - Qeff * cos(2.0*(phi - beta)))
			+ P * V * eta * kappa / (t * q) * sin(phi);

		if (dist_u(gen) < bracket) {
			double theta = eta / gamma;
			//std::cout<<"ANGLE "<<theta<<std::endl;
			return {theta * cos(phi), theta * sin(phi)}; 
		}
	}
} 
