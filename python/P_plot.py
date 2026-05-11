import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import re

# ===== НАСТРОЙКИ =====
data_dir = "fit_params"

# Истинные значения параметров
P_true = 0.5
# =====================

# Регулярное выражение для извлечения x и y из имени файла
#pattern = re.compile(r"300_(\d+)\.txt")
pattern = re.compile(r"(\d+)_49\.txt")

# Словарь для хранения данных: ключ = x, значение = [P, err_P]
data = {}

# Ищем все .txt файлы
for filepath in glob.glob(os.path.join(data_dir, "*.txt")):
    filename = os.path.basename(filepath)
    match = pattern.match(filename)
    if match:
        x = int(match.group(1))
        
        with open(filepath, 'r') as f:
               lines = f.readlines()
               if len(lines) >= 3:
                   parts_P = lines[0].split('#')[0].strip().split()
                   parts_Q = lines[1].split('#')[0].strip().split()
                   parts_beta = lines[2].split('#')[0].strip().split()
                    
                   P = float(parts_P[0])
                   err_P = float(parts_P[1]) if len(parts_P) > 1 else 0.0
                    
                    
                   data[x] = (P, err_P)

if not data:
    print(f"Не найдено файлов")
    exit()

# Сортируем по x
xs = sorted(data.keys())
print(xs)
# Вычисляем отклонения
dev_P = [P_true - data[x][0] for x in xs]

err_P = [data[x][1] for x in xs]

coef = np.polyfit(xs, dev_P,0)
c = coef

P_fit = np.polyval(coef, xs)

# Создаём графики
plt.errorbar(xs, dev_P, yerr=err_P, fmt='o', capsize=3, 
                 color='blue', markersize=3)
plt.plot(xs, P_fit, '-', color='red', linewidth=2)
plt.ylabel('P_true - P', fontsize=12)
plt.xlabel(r'$\sigma_{x^{\prime}},$ мкрад', fontsize=12)
plt.grid(True, alpha=0.3)
# Заголовок
title_line = r'$\sigma_{y^{\prime}} = 50$ мкрад'
plt.suptitle(title_line + '\n', fontsize=14, fontweight='bold')
plt.tight_layout()

# Сохраняем
output_filename = 'gr.png'
plt.savefig(output_filename, dpi=150, bbox_inches='tight')
print(f"Saved: {output_filename}")

print(c)
plt.show()

