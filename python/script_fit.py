import numpy as np
import os
import matplotlib.pyplot as plt
import subprocess
base_path = "../"
available_dirs = [d for d in os.listdir(base_path) if d.startswith("output_") and os.path.isdir(os.path.join(base_path,d))]
length = len(available_dirs)

for i in range(length):
    pars = available_dirs[i].replace("output_", "").split("_")
    subprocess.run(["python3", "fit.py", base_path + available_dirs[i]])
'''    file = open(f"fit_params/{pars[0]}_{pars[1]}.txt", "r")
    #порядок: P, Q, beta
    fit_P = file.readline()
    fit_Q = file.readline()
    fit_beta = file.readline()

    file.close() '''

