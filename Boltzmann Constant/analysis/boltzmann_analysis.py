from __future__ import annotations

import csv
import math
import shutil
import zipfile
from xml.etree import ElementTree as ET
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_output"
FIG_OUT = ROOT / "ReportFigures"
DATA_RAW = ROOT / "Data_Raw"
RAW_FIG = ROOT / "Fig"

OUT.mkdir(exist_ok=True)
FIG_OUT.mkdir(exist_ok=True)


# Transcribed from "Experimental data of thermal noise measurement.pdf".
# Frequency is in kHz and V0 is the oscilloscope RMS output in mV.
CALIBRATION_SCAN = [
    (0.5, 0.624),
    (1.0, 3.69),
    (1.5, 6.397),
    (2.0, 5.519),
    (3.0, 5.755),
    (4.0, 12.47),
    (5.0, 29.04),
    (6.0, 58.93),
    (7.0, 97.59),
    (8.0, 140.7),
    (9.0, 179.9),
    (10.0, 215.6),
    (11.0, 243.6),
    (12.0, 268.9),
    (13.0, 289.2),
    (14.0, 304.5),
    (15.0, 316.9),
    (16.0, 325.7),
    (17.0, 332.8),
    (18.0, 337.6),
    (19.0, 334.2),
    (21.0, 349.2),
    (22.0, 350.9),
    (23.0, 352.0),
    (24.0, 353.8),
    (25.0, 354.8),
    (26.0, 355.5),
    (27.0, 357.7),
    (28.0, 358.0),
    (29.0, 358.4),
    (30.0, 360.5),
    (31.0, 361.0),
    (32.0, 362.5),
    (33.0, 363.1),
    (34.0, 363.4),
    (35.0, 364.2),
    (36.0, 364.2),
    (37.0, 364.5),
    (38.0, 365.2),
    (39.0, 365.5),
    (40.0, 366.1),
    (41.0, 365.7),
    (42.0, 366.4),
    (43.0, 366.9),
    (44.0, 367.2),
    (45.0, 368.1),
    (46.0, 368.6),
    (47.0, 369.0),
    (48.0, 369.4),
    (49.0, 367.9),
    (50.0, 367.3),
    (51.0, 366.6),
    (52.0, 365.4),
    (53.0, 365.9),
    (54.0, 365.0),
    (55.0, 364.5),
    (56.0, 364.1),
    (57.0, 363.8),
    (58.0, 362.5),
    (59.0, 360.5),
    (60.0, 359.5),
    (61.0, 358.8),
    (62.0, 358.0),
    (63.0, 356.6),
    (64.0, 355.0),
    (65.0, 353.7),
    (66.0, 351.8),
    (67.0, 350.5),
    (68.0, 348.7),
    (69.0, 346.0),
    (70.0, 344.4),
    (71.0, 342.3),
    (72.0, 341.2),
    (73.0, 339.2),
    (74.0, 335.6),
    (75.0, 331.4),
    (76.0, 330.7),
    (77.0, 328.8),
    (78.0, 327.8),
    (79.0, 325.0),
    (80.0, 321.5),
]

# Calibration input RMS values written on the first scanned page, in microvolt.
VI_REPEATS_UV = [272.2, 257.0, 261.5, 273.3, 250.3, 318.9, 261.7, 279.1, 300.5, 260.0]

# Oscilloscope RMS values transcribed from the grouped photographs, in mV.
# The exact display values fluctuate; the report uses group statistics.
NOISE_RMS_MV = {
    "normal_temperature": [7.225, 7.789, 7.612, 7.478, 7.681, 7.900, 8.030, 7.966, 8.001, 7.884, 7.736, 7.641, 7.590, 7.812],
    "heated_short": [3.12, 3.25, 3.04, 3.30, 3.16, 3.28, 3.35, 3.18, 3.22],
    "heated_resistor": [6.520, 8.214, 5.668, 5.825, 6.230, 6.125, 6.502, 6.230, 5.344],
}

K_B = 1.380649e-23
RESISTOR_OHM = 10_000.0
T_HEATED_K = 57.2 + 273.15
CONTACT_CAPACITANCE_F = 0.0


def read_excel_tail() -> list[tuple[float, float]]:
    path = DATA_RAW / "V_i.xlsx"
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("xl/worksheets/sheet1.xml")
    root = ET.fromstring(xml)

    rows: list[list[float]] = []
    for row in root.findall(".//x:sheetData/x:row", ns):
        values: list[float] = []
        for cell in row.findall("x:c", ns):
            value_node = cell.find("x:v", ns)
            if value_node is not None and value_node.text:
                values.append(float(value_node.text))
        rows.append(values)
    freqs, vals = rows[0], rows[1]
    return list(zip(freqs, vals))


def write_csv(path: Path, header: list[str], rows: list[tuple]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def copy_report_figures() -> None:
    mapping = {
        RAW_FIG / "Heating_Short_Circuit_Data" / "微信图片_20260401125010.jpg": FIG_OUT / "heater_temperature.jpg",
        RAW_FIG / "Normal_Temperature_1" / "微信图片_20260401125517.jpg": FIG_OUT / "normal_noise_example.jpg",
        RAW_FIG / "Heating_Short_Circuit_Data" / "微信图片_20260401125017.jpg": FIG_OUT / "heated_short_example.jpg",
        RAW_FIG / "Heating_Normal_Circuit_Data" / "微信图片_20260401125658.jpg": FIG_OUT / "heated_resistor_example.jpg",
    }
    for src, dst in mapping.items():
        shutil.copyfile(src, dst)


def latex_table(rows: list[tuple], columns: int = 4) -> str:
    chunks = [rows[i : i + columns] for i in range(0, len(rows), columns)]
    lines = ["\\begin{tabular}{%s}" % ("cc" * columns), "\\toprule"]
    header = []
    for _ in range(columns):
        header.extend(["$f$/kHz", "$V_0$/mV"])
    lines.append(" & ".join(header) + r"\\")
    lines.append("\\midrule")
    for chunk in chunks:
        cells = []
        for f, v in chunk:
            cells.extend([f"{f:g}", f"{v:.3g}"])
        while len(cells) < columns * 2:
            cells.extend(["", ""])
        lines.append(" & ".join(cells) + r"\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines)


def main() -> None:
    copy_report_figures()

    excel_tail = read_excel_tail()
    calibration = sorted(CALIBRATION_SCAN + excel_tail)
    vi_mean_uv = float(np.mean(VI_REPEATS_UV))
    vi_std_uv = float(np.std(VI_REPEATS_UV, ddof=1))
    vi_mean_mv = vi_mean_uv / 1000.0

    freq_hz = np.array([f for f, _ in calibration]) * 1000.0
    v0_mv = np.array([v for _, v in calibration])
    gain = v0_mv / vi_mean_mv
    rc_weight = 1.0 / (1.0 + (2.0 * math.pi * freq_hz * CONTACT_CAPACITANCE_F) ** 2)
    integrand = gain**2 * rc_weight
    G_hz = float(np.trapezoid(integrand, freq_hz))

    write_csv(OUT / "calibration_curve.csv", ["frequency_kHz", "V0_mV", "gain"], [(f, v, g) for (f, v), g in zip(calibration, gain)])

    noise_rows = []
    for group, values in NOISE_RMS_MV.items():
        arr = np.array(values)
        noise_rows.append((group, len(values), float(np.mean(arr)), float(np.std(arr, ddof=1)), float(np.mean(arr**2))))
    write_csv(OUT / "noise_groups.csv", ["group", "n", "mean_rms_mV", "std_rms_mV", "mean_square_mV2"], noise_rows)

    heated = np.array(NOISE_RMS_MV["heated_resistor"])
    short = np.array(NOISE_RMS_MV["heated_short"])
    vj2_mV2 = float(np.mean(heated**2) - np.mean(short**2))
    vj2_V2 = vj2_mV2 * 1e-6
    vj_rms_mV = math.sqrt(max(vj2_mV2, 0.0))
    k_measured = vj2_V2 / (4.0 * T_HEATED_K * RESISTOR_OHM * G_hz)
    k_relative_error = (k_measured - K_B) / K_B
    r_eff_ohm = vj2_V2 / (4.0 * K_B * T_HEATED_K * G_hz)

    summary = {
        "vi_mean_uv": vi_mean_uv,
        "vi_std_uv": vi_std_uv,
        "calibration_points": len(calibration),
        "G_hz": G_hz,
        "heated_temperature_K": T_HEATED_K,
        "vj2_mV2": vj2_mV2,
        "vj_rms_mV": vj_rms_mV,
        "resistor_ohm": RESISTOR_OHM,
        "k_measured": k_measured,
        "k_relative_error": k_relative_error,
        "r_eff_ohm": r_eff_ohm,
    }
    write_csv(OUT / "summary.csv", ["quantity", "value"], list(summary.items()))

    plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=180)
    ax.plot([f for f, _ in calibration], v0_mv, "o-", ms=3.2, lw=1.2)
    ax.set_xlabel("频率 f / kHz")
    ax.set_ylabel("输出有效值 V0 / mV")
    ax.set_title("测量系统校准曲线")
    ax.grid(True, alpha=0.28)
    fig.tight_layout()
    fig.savefig(OUT / "calibration_curve.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=180)
    ax.plot([f for f, _ in calibration], gain, "o-", ms=3.0, lw=1.1, color="#006d77")
    ax.set_xlabel("频率 f / kHz")
    ax.set_ylabel("有效增益 g(f)")
    ax.set_title("有效增益随频率变化")
    ax.grid(True, alpha=0.28)
    fig.tight_layout()
    fig.savefig(OUT / "gain_curve.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=180)
    ax.plot([f for f, _ in calibration], integrand / 1e6, "o-", ms=3.0, lw=1.1, color="#8f2d56")
    ax.fill_between([f for f, _ in calibration], integrand / 1e6, alpha=0.16, color="#8f2d56")
    ax.set_xlabel("频率 f / kHz")
    ax.set_ylabel(r"$g(f)^2$ / $10^6$")
    ax.set_title("增益积分的被积函数（C=0）")
    ax.grid(True, alpha=0.28)
    fig.tight_layout()
    fig.savefig(OUT / "gain_integrand.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=180)
    labels = ["常温接入", "加热短路", "加热接入"]
    means = [
        np.mean(NOISE_RMS_MV["normal_temperature"]),
        np.mean(NOISE_RMS_MV["heated_short"]),
        np.mean(NOISE_RMS_MV["heated_resistor"]),
    ]
    stds = [
        np.std(NOISE_RMS_MV["normal_temperature"], ddof=1),
        np.std(NOISE_RMS_MV["heated_short"], ddof=1),
        np.std(NOISE_RMS_MV["heated_resistor"], ddof=1),
    ]
    ax.bar(labels, means, yerr=stds, capsize=4, color=["#4c78a8", "#f58518", "#54a24b"])
    ax.set_ylabel("示波器 RMS / mV")
    ax.set_title("噪声有效值分组统计")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "noise_groups.png")
    plt.close(fig)

    with (OUT / "tables.tex").open("w", encoding="utf-8") as f:
        f.write("% Auto-generated by analysis/boltzmann_analysis.py\n")
        f.write("\\newcommand{\\ViMeanUv}{%.1f}\n" % vi_mean_uv)
        f.write("\\newcommand{\\ViStdUv}{%.1f}\n" % vi_std_uv)
        f.write("\\newcommand{\\CalibrationPointCount}{%d}\n" % len(calibration))
        f.write("\\newcommand{\\GainIntegral}{%.3e}\n" % G_hz)
        f.write("\\newcommand{\\HeatedTemperatureK}{%.2f}\n" % T_HEATED_K)
        f.write("\\newcommand{\\JohnsonSquareMv}{%.2f}\n" % vj2_mV2)
        f.write("\\newcommand{\\JohnsonRmsMv}{%.2f}\n" % vj_rms_mV)
        f.write("\\newcommand{\\ResistorOhm}{%.0f}\n" % RESISTOR_OHM)
        f.write("\\newcommand{\\ResistorKOhm}{%.2f}\n" % (RESISTOR_OHM / 1000.0))
        f.write("\\newcommand{\\MeasuredBoltzmann}{%.3e}\n" % k_measured)
        f.write("\\newcommand{\\BoltzmannRelativeError}{%.2f}\n" % (k_relative_error * 100.0))
        f.write("\\newcommand{\\EffectiveResistance}{%.2e}\n" % r_eff_ohm)
        f.write("\\newcommand{\\EffectiveResistanceKOhm}{%.2f}\n" % (r_eff_ohm / 1000.0))
        f.write("\\newcommand{\\CalibrationTable}{%\n")
        f.write(latex_table(calibration))
        f.write("\n}\n")
        f.write("\\newcommand{\\NoiseGroupTable}{%\n")
        f.write("\\begin{tabular}{lrrrr}\\toprule\n")
        f.write("分组 & 读数个数 & 平均 RMS/mV & 标准差/mV & 均方/mV$^2$\\\\\\midrule\n")
        names = {
            "normal_temperature": "常温接入电阻",
            "heated_short": "加热短路本底",
            "heated_resistor": "加热接入电阻",
        }
        for group, n, mean, std, ms in noise_rows:
            f.write(f"{names[group]} & {n} & {mean:.3f} & {std:.3f} & {ms:.2f}\\\\\n")
        f.write("\\bottomrule\\end{tabular}\n")
        f.write("}\n")

    print("calibration points", len(calibration))
    print("Vi mean/std uV", vi_mean_uv, vi_std_uv)
    print("G Hz", G_hz)
    print("Vj rms mV", vj_rms_mV)
    print("k measured", k_measured)
    print("k relative error", k_relative_error)
    print("R_eff ohm", r_eff_ohm)


if __name__ == "__main__":
    main()
