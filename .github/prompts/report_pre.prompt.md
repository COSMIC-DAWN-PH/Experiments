---
description: "Preprocess a physics experiment report with the report_pre workflow"
name: "report_pre"
argument-hint: "Experiment Folder PDF Manual LaTeX Template"
agent: "agent"
---

Use the report_pre workflow for a physics experiment report.

If the user has not provided all required inputs, ask for:
- Experiment Folder
- PDF Manual filename
- LaTeX Template path

Then follow the workflow in `.agents/skills/report_pre/SKILL.md`:
1. Run `python workflow_preprocess.py "<Experiment Folder>" "<PDF Manual>"`
2. Read `<Experiment Folder>/extracted_manual.txt`
3. Fill the LaTeX template in `<Experiment Folder>`
4. Keep the `Data Processing` section empty
5. Verify LaTeX environments are balanced before finishing