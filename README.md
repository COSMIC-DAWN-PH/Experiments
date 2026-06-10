# Comprehensive Physics Experiments (综合物理实验)

UCAS 大二春季学期综合物理实验 I 课程的实验报告与数据记录仓库。

## 实验列表

| 实验 | 目录 | 说明 |
|------|------|------|
| Boltzmann Constant | `Boltzmann Constant/` | 热噪声法测量玻尔兹曼常数 |
| Brownian Movement | `Brownian movement/` | 布朗运动实验 |
| Elliptic Polarization | `Elliptic Polarization/` | 椭偏法测定介质薄膜厚度和折射率 |
| Ising Model | `Ising Model/` | 伊辛模型蒙特卡罗模拟 |
| Weak Current Measurement | `Weak Current Measurement/` | 弱电流测量 (Al-Zn) |

## 目录结构

```
├── Template.tex                    # LaTeX 实验报告模板
├── workflow_preprocess.py          # 自动化预处理脚本
├── Report_Automation_Workflow.md   # 报告自动化工作流说明
├── wrting.md                       # 实验报告写作规范
├── Boltzmann Constant/             # 玻尔兹曼常数实验
│   ├── Fig/                        #   实验图片
│   ├── V_i.xlsx                    #   实验数据
│   ├── Handouts.pdf                #   实验讲义
│   └── Experimental data of ...pdf #   实验数据 PDF
├── Brownian movement/              # 布朗运动实验
│   └── 布朗运动实验数据/            #   实验原始数据
├── Elliptic Polarization/          # 椭偏法实验
│   ├── Elliptic Polarization.tex   #   实验报告 (LaTeX)
│   ├── Figure/                     #   实验图片
│   └── Original Data/              #   原始数据
├── Ising Model/                    # 伊辛模型实验
│   ├── Ising Model.tex             #   实验报告 (LaTeX)
│   ├── Figure/                     #   实验图片
│   └── extracted_manual.txt        #   提取的实验手册文本
└── Weak Current Measurement/       # 弱电流测量实验
    ├── AlZnRecord/                 #   Al-Zn 数据记录 (LaTeX)
    ├── AlZnRecordFig/              #   数据汇总图
    ├── record.tex                  #   实验记录 (LaTeX)
    └── run_fit.py                  #   数据拟合脚本 (Python)
```

## 工作流

每个实验报告的生成遵循以下步骤：

1. **预处理** — 运行 `workflow_preprocess.py` 自动重命名图片、提取 PDF 文本
2. **AI 辅助生成** — 基于 `wrting.md` 中的写作规范，使用 AI 生成 LaTeX 报告框架
3. **数据处理与编译** — 填充实验数据，编译生成最终 PDF

详见 [Report_Automation_Workflow.md](Report_Automation_Workflow.md)。

## 技术栈

- **LaTeX** — 实验报告排版 (XeLaTeX + ctex)
- **Python** — 数据处理与拟合 (NumPy, Matplotlib, SciPy)
- **Excel** — 原始实验数据记录
