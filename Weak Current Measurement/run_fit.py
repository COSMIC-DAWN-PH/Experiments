import numpy as np
import matplotlib.pyplot as plt
import os

# Data extracted from tex
times = np.arange(0, 520, 5)
currents = np.array([
    3.97238, 3.91674, 3.92095, 3.90716, 3.89428, 3.88444, 3.87976, 3.87532, 3.88543, 3.88693,
    3.87926, 3.87065, 3.85999, 3.84749, 3.83627, 3.83665, 3.83604, 3.83665, 3.83599, 3.83338,
    3.82815, 3.82213, 3.81653, 3.80733, 3.79017, 3.78885, 3.79569, 3.79045, 3.78471, 3.77857,
    3.77306, 3.76839, 3.76519, 3.76386, 3.76236, 3.76451, 3.76463, 3.76508, 3.76704, 3.77111,
    3.77176, 3.76843, 3.76126, 3.75172, 3.73845, 3.72580, 3.70905, 3.69834, 3.68166, 3.66699,
    3.64651, 3.63222, 3.61547, 3.59946, 3.58491, 3.57439, 3.56165, 3.55052, 3.53915, 3.52836,
    3.51963, 3.50969, 3.49985, 3.49226, 3.48674, 3.48026, 3.47116, 3.46564, 3.45540, 3.44574,
    3.43888, 3.43044, 3.42525, 3.41990, 3.40930, 3.40139, 3.39305, 3.38416, 3.37527, 3.36089,
    3.35198, 3.33689, 3.32940, 3.31483, 3.30596, 3.29571, 3.28770, 3.27870, 3.27111, 3.26191,
    3.25512, 3.24895, 3.24176, 3.23388, 3.22611, 3.21889, 3.20643, 3.19768, 3.19186, 3.18392,
    3.17543, 3.16556, 3.15671, 3.14324
])

popt = np.polyfit(times, currents, 2)
p1d = np.poly1d(popt)

all_times = np.arange(0, 905, 5)
all_currents = []
for t in all_times:
    if t <= times[-1]:
        all_currents.append(currents[np.where(times == t)[0][0]])
    else:
        all_currents.append(p1d(t))

all_currents = np.array(all_currents)

with open('data_table.tex', 'w', encoding='utf-8') as f:
    f.write(r'\begin{table}[ht]' + '\n')
    f.write(r'\centering' + '\n')
    f.write(r'\caption{随时间变化的电流测量值（含拟合预测至900s）}' + '\n')
    f.write(r'\label{tab:current_data}' + '\n')
    f.write(r'\resizebox{\textwidth}{!}{' + '\n')
    f.write(r'\begin{tabular}{cc|cc|cc|cc|cc|cc}' + '\n')
    f.write(r'\toprule' + '\n')
    f.write(r'时间(s) & 电流(nA) & 时间(s) & 电流(nA) & 时间(s) & 电流(nA) & 时间(s) & 电流(nA) & 时间(s) & 电流(nA) & 时间(s) & 电流(nA) \\' + '\n')
    f.write(r'\midrule' + '\n')
    num_rows = int(np.ceil(len(all_times) / 6.0))
    for i in range(num_rows):
        row_str = []
        for j in range(6):
            idx = j * num_rows + i
            if idx < len(all_times):
                row_str.append(f'{all_times[idx]:d} & {all_currents[idx]:.4f}')
            else:
                row_str.append(' & ')
        f.write(' & '.join(row_str) + r' \\' + '\n')
    f.write(r'\bottomrule' + '\n')
    f.write(r'\end{tabular}' + '\n')
    f.write(r'}' + '\n')
    f.write(r'\end{table}' + '\n')

plt.figure(figsize=(8, 6))
plt.scatter(times, currents, s=10, label='Experimental Data', color='blue')
plt.plot(all_times, p1d(all_times), label=f'Fit: $I(t)={popt[0]:.2e}t^2 + {popt[1]:.2e}t + {popt[2]:.2f}$', color='red', linestyle='--')
plt.xlabel('Time (s)')
plt.ylabel('Current (nA)')
plt.title('Al-Cu Electrolysis Current vs Time')
plt.legend()
plt.grid(True)
path = r"c:\Personal Profie\Profile\UCAS\t-Sophomore\S2\综合物理实验\弱电流测量\fit_plot.png"
plt.savefig(path)
print('Function params:', popt)
