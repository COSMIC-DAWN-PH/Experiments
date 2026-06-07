# Writing Skill: Physics Experiment Report Automation

## Context and Goal
This skill automates the process of generating a LaTeX physics experiment report from a provided PDF manual and a set of screenshot images. It ensures the experiment document is properly populated while preserving the user's original template formatting.

## Workflow

When tasked with completing an experiment report (and told to use this skill), execute the following steps in order:

### 1. Document Reading & Information Extraction
- Read the provided `.tex` template file to understand the current structure and where to insert information.
- Extract the text content from the provided `.pdf` experiment manual (using tools like `pdftotext` or a python script).
- Identify and extract the following key components from the PDF:
  - Experiment Name
  - Experiment Objective (实验目的)
  - Experiment Apparatus (实验仪器与用具)
  - Theoretical Principles (实验原理)
  - Experimental Procedure (实验内容)
  - Thought Questions (思考题)

### 2. Pre-processing the Image Assets
- Navigate to the `Figure` folder within the experiment directory.
- Rename the image files (which are usually auto-generated screenshots named with spaces and timestamps, e.g., "屏幕截图 2026-05-04...") to sequential English names like `fig1.png`, `fig2.png`, etc., based on their chronological generation order. This prevents LaTeX compilation errors caused by Chinese characters or spaces in file paths.

### 3. LaTeX Content Generation & Population
Use precise file modification tools (like `multi_replace_file_content` or `replace_file_content`) to populate the `.tex` file without altering the predefined header template (e.g., author info, date) or the core section structure (`\section{...}`).

#### 3.1 Basic Information & Expansion
- Update the `\experiName` command with the correct experiment title.
- **实验目的 (Objective)**: Expand the PDF's objective into a detailed `enumerate` list. Include cognitive, theoretical, and practical skill goals.
- **实验仪器与用具 (Apparatus)**: Expand the apparatus list into a detailed `itemize` list, detailing the function and specific role of each piece of equipment (e.g., Polarizer, 1/4 waveplate, etc.).

#### 3.2 Theory & Procedure Transcription
- **实验原理 (Theory)**: Transcribe the theoretical background from the PDF into LaTeX format. Convert all mathematical formulas into appropriate LaTeX math environments (`equation`, `align`).
- **实验内容 (Procedure)**: Convert the experimental steps into a clean `enumerate` list.
- **思考题 (Questions)**: Copy the thought questions into an `enumerate` list at the end of the document.

#### 3.3 Image Integration
- Determine the exact logical position of each figure based on the context of the PDF's flow.
- Insert the renamed images (`Figure/fig1.png`, etc.) using the `figure` environment with the `[H]` float specifier:
  ```latex
  \begin{figure}[H]
      \centering
      \includegraphics[width=0.6\textwidth]{Figure/figX.png} % Adjust width as needed
      \caption{<Extracted Caption from PDF>}
  \end{figure}
  ```
- Distribute the images correctly across the **实验原理** (Theory) and **实验内容** (Procedure) sections exactly where they were referenced or meant to appear in the PDF.

#### 3.4 Final Touches
- Leave the **实验数据处理 (Data Processing)** section blank for the user to fill out their measured data later.

## Constraints & Rules
- **DO NOT** modify the personal information fields or document headers in the `.tex` file.
- **DO NOT** delete or alter the predefined `\section` headers.
- Always ensure LaTeX math syntax is perfectly formed to prevent compilation errors.
