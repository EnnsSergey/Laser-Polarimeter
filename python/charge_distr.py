import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

directory = '../output_pb_12/'

charge = np.loadtxt(directory + 'charge.txt')
print("максимум ", max(charge))
print("минимум ", min(charge))
print("всего ", len(charge))
kde = gaussian_kde(charge)

q = np.linspace(min(charge)-0.5, max(charge)+0.5, 1000)
y = kde(q)
print("Макушка: ", round(q[np.argmax(y)]))
threshold = max(y) * 0.01
mask = y > threshold
q_crop = q[mask]
y_crop = y[mask]
plt.plot(q_crop, y_crop)
plt.xlabel("Заряд")
plt.ylabel("Плотность вероятности")
plt.show()
plt.savefig("distr.png")
