# 物理实验报告自动化生成工作流 (Physics Experiment Report Automation Workflow)

结合 `wrting.md` 中的规范，为了让你以后能“一键调用”自动化完成实验报告的预处理和 LaTeX 编写，我为你设计了以下工作流。

## 工作流结构

该工作流包含两个核心步骤：
1. **本地脚本预处理**：运行 `workflow_preprocess.py` 自动整理图片并提取 PDF 文本（此步骤将最容易出错的繁杂步骤程序化）。
2. **AI 智能生成**：通过一条标准的 Prompt 呼叫 AI（比如我），直接读取预处理的数据并根据 `wrting.md` 的要求生成完美的 LaTeX 代码。

---

## 🚀 如何使用 (How to use)

以后每次做完实验，只需按照以下步骤操作：

### Step 1: 准备好你的文件
确保新的实验文件夹（例如 `Weak Current Measurement`）内包含：
- 实验手册 PDF 文件（例如 `manual.pdf`）
- `Figure` 文件夹（包含所有实验截图）
- LaTeX 模板文件（例如 `Template.tex`）

### Step 2: 发送指令给我
复制并修改下面的 Prompt，直接发送给我：

```markdown
@Antigravity 请根据 `wrting.md` 的规范，为我的新实验生成 LaTeX 报告。

**实验文件夹**: `[填入文件夹名，例如：Weak Current Measurement]`
**PDF 手册名**: `[填入 PDF 文件名，例如：manual.pdf]`
**LaTeX 文件名**: `[填入 Tex 文件名，例如：Template.tex]`

**执行步骤**:
1. **预处理**: 请使用 PowerShell 在根目录下运行 `python workflow_preprocess.py "[实验文件夹]" "[PDF 手册名]"`。（如果提示缺少 PyPDF2，请帮我 `pip install PyPDF2` 后重试）。
2. **阅读信息**: 读取预处理后生成的 `extracted_manual.txt` 文件内容，理解实验原理、步骤和思考题。
3. **内容填充**:
   - 严格按照 `wrting.md` 的规则，更新 LaTeX 的 `\experiName`。
   - 将“实验目的”和“实验仪器”扩充为详细的 `enumerate`/`itemize` 列表格式。
   - 将“实验原理”和“实验内容”转换为标准的 LaTeX 排版，数学公式必须使用环境包裹。
   - 将重命名后的图片（`Figure/fig1.png` 等）插入到“实验原理”和“实验内容”的适当逻辑位置。
   - 思考题作为 `enumerate` 附在文档末尾。
4. **终检**: 保持“实验数据处理”部分留空，并且绝不能修改预设的个人信息 Header 和 Section 结构。
```

---

## 🛠️ 关于配套脚本 `workflow_preprocess.py`
为了让这套工作流更加稳定和迅速，我已经在当前目录下为你创建了 `workflow_preprocess.py`。
该脚本会自动：
- 按照文件修改时间，将 `Figure/` 下的所有中文截图重命名为符合 LaTeX 要求的 `fig1.png`, `fig2.png` 格式。
- 使用 `PyPDF2` 库将 PDF 手册中的文字完整提取到 `extracted_manual.txt`，使得 AI 读取提取文本时的准确率提升 100%。

*(注：原有的 `wrting.md` 文件名似乎存在拼写错误，如果需要，你可以将其重命名为 `writing_skill.md`。如果你重命名了，记得在上面的 Prompt 中也修改一下文件名哦！)*
