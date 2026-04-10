#include "run.hh"
#include <filesystem>


RunAction::RunAction(int thr_num, Params params) : thr_num(thr_num), fParams(params)
{
	for(auto& row : histogram_r)
		row.fill(0);

	for(auto& row : histogram_l)
		row.fill(0);

}

RunAction::~RunAction()
{}

void RunAction::BeginOfRunAction(const G4Run* run)
{
	for(auto& row : histogram_r)
		row.fill(0);
 
	for(auto& row : histogram_l)
		row.fill(0);
}
void RunAction::EndOfRunAction(const G4Run*)
{
std::string pth = "/home/enns/LaserPolarimeter/";
std::filesystem::path dir = "output_" + std::to_string(static_cast<int>((fParams.d_theta_x * pow(10,6)))) + "_" + std::to_string(static_cast<int>(fParams.d_theta_y * pow(10,6)));

std::filesystem::path full_path = pth;
full_path /= dir;

std::filesystem::create_directory(full_path);

std::ofstream outFile;
std::filesystem::path hist_r_path = full_path / ("histogram_r_" + std::to_string(thr_num) + ".txt");
outFile.open(hist_r_path);

std::cout << "ПУТЬ " << hist_r_path << std::endl;
G4cout << "=== ГИСТОГРАММА ЗАРЯДОВ ДЛЯ ПРАВОЙ ПОЛЯРИЗАЦИИ ===" << G4endl;

for(int i = 0; i < ReadOut::YSIZE; i++)
{
    for(int j = 0; j < ReadOut::XSIZE; j++)
    {
        G4cout << histogram_r[i][j] << " ";
        if(j < ReadOut::XSIZE) 
            outFile << histogram_r[i][j] << " ";
    }
    G4cout << G4endl;
    outFile << std::endl;
}
outFile.close();



std::filesystem::path hist_l_path = full_path / ("histogram_l_" + std::to_string(thr_num) + ".txt");
outFile.open(hist_l_path);

std::cout << "ПУТЬ " << hist_l_path << std::endl;
G4cout << "=== ГИСТОГРАММА ЗАРЯДОВ ДЛЯ ЛЕВОЙ ПОЛЯРИЗАЦИИ ===" << G4endl;

for(int i = 0; i < ReadOut::YSIZE; i++)
{
    for(int j = 0; j < ReadOut::XSIZE; j++)
    {
        G4cout << histogram_l[i][j] << " ";
        if(j < ReadOut::XSIZE) 
            outFile << histogram_l[i][j] << " ";
    }
    G4cout << G4endl;
    outFile << std::endl;
}
outFile.close();
}

