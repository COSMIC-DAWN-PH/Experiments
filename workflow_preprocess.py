import os
import sys
import glob

def rename_figures(experiment_dir):
    figure_dir = os.path.join(experiment_dir, "Figure")
    if not os.path.exists(figure_dir):
        print(f"  [-] No Figure folder found at {figure_dir}")
        return

    extensions = ('*.png', '*.jpg', '*.jpeg')
    image_files = []
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(figure_dir, ext)))
    
    if not image_files:
        print("  [-] No images found in Figure folder.")
        return

    # Sort by creation/modification time
    image_files.sort(key=os.path.getmtime)

    print(f"  [+] Found {len(image_files)} images. Renaming...")
    for i, file_path in enumerate(image_files):
        ext = os.path.splitext(file_path)[1]
        new_name = f"fig{i+1}{ext}"
        new_path = os.path.join(figure_dir, new_name)
        
        if os.path.basename(file_path) == new_name:
            continue
            
        os.rename(file_path, new_path)
        print(f"    -> Renamed: {os.path.basename(file_path)} to {new_name}")

def extract_pdf_text(experiment_dir, pdf_filename):
    pdf_path = os.path.join(experiment_dir, pdf_filename)
    if not os.path.exists(pdf_path):
        print(f"  [-] PDF file not found at {pdf_path}")
        return
        
    output_path = os.path.join(experiment_dir, "extracted_manual.txt")
    
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
                
        with open(output_path, 'w', encoding='utf-8') as out_file:
            out_file.write(text)
        print(f"  [+] PDF text successfully extracted to {output_path}")
    except ImportError:
        print("  [-] PyPDF2 is not installed. Please run `pip install PyPDF2` to enable automatic PDF text extraction.")
    except Exception as e:
        print(f"  [-] Error extracting PDF: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python workflow_preprocess.py <experiment_folder_path> <pdf_filename>")
        print("Example: python workflow_preprocess.py \"Weak Current Measurement\" \"manual.pdf\"")
        sys.exit(1)
        
    exp_dir = sys.argv[1]
    pdf_name = sys.argv[2]
    
    if not os.path.exists(exp_dir):
        print(f"Error: Directory '{exp_dir}' does not exist.")
        sys.exit(1)
        
    print(f"Starting Pre-processing for {exp_dir}...")
    rename_figures(exp_dir)
    extract_pdf_text(exp_dir, pdf_name)
    print("Pre-processing complete.")
