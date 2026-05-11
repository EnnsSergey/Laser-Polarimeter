import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import re
from scipy.optimize import curve_fit

data_dir = "fit_params"

# Регулярное выражение для извлечения x из имени файла
pattern = re.compile(r"pb_(\d+)\.txt")

# Словарь для хранения данных
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
                
                Q = float(parts_Q[0])
                err_Q = float(parts_Q[1]) if len(parts_Q) > 1 else 0.0
                
                beta = float(parts_beta[0])
                err_beta = float(parts_beta[1]) if len(parts_beta) > 1 else 0.0
                
                data[x] = (P, Q, beta, err_P, err_Q, err_beta)

if not data:
    print("Не найдено файлов")
    exit()

# Сортируем по x
xs = sorted(data.keys())
print("Толщины (мм):", xs)

# Подогнанные параметры
fit_P = [data[x][0] for x in xs]
err_P = [data[x][3] for x in xs]

P_fit = np.array(fit_P)
P_err = np.array(err_P)

# Эффективность (отношение сигнал/шум)
effP = P_fit / P_err

# Преобразуем в numpy array
xs = np.array(xs, dtype=float)
effP = np.array(effP, dtype=float)

print("\nЭффективность P*/σ_P*:", effP)
