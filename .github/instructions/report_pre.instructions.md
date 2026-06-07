---
description: "Use when preprocessing physics experiment reports, extracting manual text, and filling LaTeX templates. Mentions report_pre, workflow_preprocess.py, extracted_manual.txt, and LaTeX template population."
name: "report_pre"
---

# report_pre Workflow Guidance

- Use this guidance when the task involves a physics experiment report, especially `report_pre`.
- Gather the Experiment Folder, PDF Manual filename, and LaTeX Template path before starting.
- Run `python workflow_preprocess.py "<Experiment Folder>" "<PDF Manual>"` first.
- Read `<Experiment Folder>/extracted_manual.txt` after preprocessing.
- Populate the LaTeX template carefully without breaking the existing document structure.
- Keep the `Data Processing` section empty.
- Check that every LaTeX environment is properly closed before finishing.