#include "run.hh"

RunAction::RunAction(int thr_num) : thr_num(thr_num)
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
	std::string directory = "/home/enns/LaserPolarimeter/output/";
	std::ofstream outFile;
	outFile.open(directory + "histogram_r_" + std::to_string(thr_num)+ ".txt");
	G4cout<<"=== ГИСТОГРАММА ЗАРЯДОВ ДЛЯ ПРАВОЙ ПОЛЯРИЗАЦИИ ==="<<G4endl;
	for(int i = 0; i < ReadOut::YSIZE; i++)
	{
		for(int j = 0; j < ReadOut::XSIZE; j++)
		{
			G4cout<<histogram_r[i][j]<<" ";
			if(j<ReadOut::XSIZE) outFile<<histogram_r[i][j]<<" ";
		}
		G4cout << G4endl;
		outFile << std::endl;
	}
	outFile.close();

	outFile.open(directory + "histogram_l_" + std::to_string(thr_num)+ ".txt");
	
	G4cout<<"=== ГИСТОГРАММА ЗАРЯДОВ ДЛЯ ЛЕВОЙ ПОЛЯРИЗАЦИИ ==="<<G4endl;
	for(int i = 0; i < ReadOut::YSIZE; i++)
	{
		for(int j = 0; j < ReadOut::XSIZE; j++)
		{
			G4cout<<histogram_l[i][j]<<" ";
			if(j<ReadOut::XSIZE) outFile<<histogram_l[i][j]<<" ";
		}
		G4cout << G4endl;
		outFile << std::endl;
	}
	outFile.close();

}

