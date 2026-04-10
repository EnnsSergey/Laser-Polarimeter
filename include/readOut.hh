#ifndef READOUT_HH
#define READOUT_HH

#include <G4Types.hh>
#include "G4SystemOfUnits.hh"
#include <array>
#include <cmath>

class ReadOut
{
    public:
        constexpr static size_t XSIZE = 32;    // 32 пада по X
        constexpr static size_t YSIZE = 20;    // 20 падов по Y
        constexpr static float X_SIZE = 64*mm; // Размер детектора по X
        constexpr static float Y_SIZE = 20*mm;  // Размер детектора по Y
        
        std::array<std::array<float, XSIZE>, YSIZE> charge;
        
        ReadOut(void)
        {
            // Инициализация нулями
            for(auto& row : charge)
                row.fill(0.0);
        }
        
        float& operator() (float x, float y) 
        {
            // Преобразование координат в индексы падов
            int j = floor(x * (XSIZE/X_SIZE)) + 0.5 * XSIZE; 
            int i = floor(y * (YSIZE/Y_SIZE)) + YSIZE * 0.5;
            
            // Проверка границ
            if(i < 0) i = 0;
            if(i >= YSIZE) i = YSIZE - 1;
            if(j < 0) j = 0;
            if(j >= XSIZE) j = XSIZE - 1;
            
            return charge[i][j];
        }
        
        void AddCharge(float x, float y, float q)
        {
            // Проверка выхода за пределы детектора
            if(std::abs(x) > 0.5*X_SIZE || std::abs(y) > 0.5*Y_SIZE) return;
            (*this)(x, y) += q;
        }
        
        void Clear()
        {
            for(auto& row : charge)
                row.fill(0.0);
        }
};

#endif
