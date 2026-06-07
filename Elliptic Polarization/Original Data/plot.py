import csv
import matplotlib.pyplot as plt

f = open('1_details.txt', encoding='gbk')
reader = csv.reader(f, delimiter='\t')
next(reader)  # Skip header

A_vals = []
I_vals = []

for r in reader:
    if len(r) > 3:
        A_vals.append(float(r[3]))
        I_vals.append(float(r[1]))

plt.figure(figsize=(8,6))
plt.plot(A_vals, I_vals, 'bo-', markersize=4)
plt.xlabel('Analyzer Angle A (deg)', fontsize=14)
plt.ylabel('Light Intensity (%)', fontsize=14)
plt.title('Light Intensity vs Analyzer Angle', fontsize=16)
plt.grid(True)
plt.savefig('../extinction_curve.pdf')
plt.close()
