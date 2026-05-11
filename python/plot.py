import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import re

# ===== НАСТРОЙКИ =====
data_dir = "fit_params"

# Истинные значения параметров
P_true = 1.0
Q_true = 0.1
beta_true = 0.7
# =====================

# Регулярное выражение для извлечения x и y из имени файла
#pattern = re.compile(r"300_(\d+)\.txt")
pattern = re.compile(r"(\d+)_49\.txt")

# Словарь для хранения данных: ключ = x, значение = [P, Q, beta, err_P, err_Q, err_beta]
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
    print(f"Не найдено файлов")
    exit()

# Сортируем по x
xs = sorted(data.keys())
print(xs)
# Вычисляем отклонения
dev_P = [P_true - data[x][0] for x in xs]
dev_Q = [Q_true - abs(data[x][1]) for x in xs]
dev_beta = [beta_true - data[x][2] for x in xs]

err_P = [data[x][3] for x in xs]
err_Q = [data[x][4] for x in xs]
err_beta = [data[x][5] for x in xs]

# Создаём графики
fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=False)

# P
axes[0].errorbar(xs, dev_P, yerr=err_P, fmt='o-', capsize=3, 
                 color='blue', linewidth=2, markersize=6)
axes[0].set_ylabel('P_true - P', fontsize=12)
axes[0].set_xlabel(r'$\sigma_{x^{\prime}},$ мкрад', fontsize=12)
axes[0].grid(True, alpha=0.3)

# Q
axes[1].errorbar(xs, dev_Q, yerr=err_Q, fmt='o-', capsize=3, 
                 color='red', linewidth=2, markersize=6)
axes[1].set_ylabel('Q_true - |Q|', fontsize=12)
axes[1].set_xlabel(r'$\sigma_{x^{\prime}},$ мкрад', fontsize=12)
axes[1].grid(True, alpha=0.3)

# beta
axes[2].errorbar(xs, dev_beta, yerr=err_beta, fmt='o-', capsize=3, 
                 color='green', linewidth=2, markersize=6)
axes[2].set_ylabel('beta_true - beta', fontsize=12)
axes[2].set_xlabel(r'$\sigma_{x^{\prime}},$ мкрад', fontsize=12)
axes[2].grid(True, alpha=0.3)

# Общий заголовок
title_line = r'Зависимость отклонений параметров от $\sigma_{x^{\prime}}$ при $\sigma_{y^{\prime}} = 50$ мкрад'
plt.suptitle(title_line + '\n', fontsize=14, fontweight='bold')
plt.tight_layout()

# Сохраняем
output_filename = 'gr.png'
plt.savefig(output_filename, dpi=150, bbox_inches='tight')
print(f"Saved: {output_filename}")

plt.show()
