import os
import subprocess
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

# Function to convert a notebook to PDF using nbconvert command line
def convert_notebook_to_pdf(notebook_path, output_pdf_path):
    output_name, _ = os.path.splitext(output_pdf_path)  # Remove the file extension from the output path
    subprocess.run([
        "jupyter", "nbconvert", "--to", "pdf", notebook_path, "--output", output_name
    ])

# Function to merge two PDFs
def merge_pdfs(output_pdf_path, pdf_paths):
    merger = PdfMerger()
    for path in pdf_paths:
        merger.append(path)
    merger.write(output_pdf_path)
    merger.close()

# Function to copy a PDF
def copy_pdf(source_pdf_path, output_pdf_path):
    reader = PdfReader(source_pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    with open(output_pdf_path, 'wb') as output_pdf:
        writer.write(output_pdf)

# Main script
def main():
    folder_path = os.path.abspath(os.getcwd())  # Change this to your folder path
    notebooks_to_print = ["train_model.ipynb", "data_features.ipynb", "temporal_features.ipynb", "visualize_errors.ipynb"]
    notebooks = set()
    
    # Identify all notebooks
    for filename in os.listdir(folder_path):
        if filename in notebooks_to_print:
            notebooks.add(filename.replace(".ipynb", ""))
    
    pdf_folder = os.path.join(folder_path, 'pdfs')
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)


    notebook_paths = [ os.path.join(folder_path, f'{notebook}.ipynb') for notebook in notebooks ]
    resulting_pdfs = [ os.path.join(pdf_folder, f'{notebook}.pdf') for notebook in notebooks ]

    combined_pdf = os.path.join(pdf_folder, f'combined_notebooks.pdf')

    for (notebook_path, resulting_pdf) in zip(notebook_paths, resulting_pdfs):
        # Convert the notebook notebook to PDF
        print(notebook_path)
        print(resulting_pdf)
        convert_notebook_to_pdf(notebook_path, resulting_pdf)
                
    # Merge the PDFs
    merge_pdfs(combined_pdf, resulting_pdfs)
    
        # Clean up the individual PDFs
    for resulting_pdf in resulting_pdfs:
        os.remove(resulting_pdf)
        
if __name__ == '__main__':
    main()
