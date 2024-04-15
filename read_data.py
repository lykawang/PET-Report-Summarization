import os
import pandas as pd
import PyPDF2
from datetime import datetime

# Directory containing PDF files
pdf_folder = 'reports_data'

# Output Excel file
output_file = 'output.xlsx'

# Function to extract text from a single PDF
def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = []
        for page in reader.pages:
            text.append(page.extract_text())
    return '\n'.join(text)

# Helper function to format date
def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%d %b %Y')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return date_str  # Return original if parsing fails

# Function to clean text from headers and page numbers
def clean_text(text):
    text = text.replace("BC Cancer Agency Transcription Text", "")
    text = text.replace("BCCA PET Scan Report", "")
    text = text.replace("PET Scan Report (MM)", "")
    text = text.replace("BC Cancer Agency - Vancouver Centre", "")
    text = text.replace("DIAGNOSTIC REPORT - PET SCAN", "")
    text = text.replace("PET Scan Report", "")
    lines = text.split('\n')
    cleaned_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('Page'):
            i += 5  # Skip this line and the next four lines
        elif not (line.startswith('MRN (Trial ID):') or line.startswith('Date of Service:') or line.startswith('Tel:')):
            cleaned_lines.append(line)
            i += 1
        else:
            i += 1
    return '\n'.join(cleaned_lines)

# Function to parse information from extracted text
def parse_information(text):
    data = {
        'Scan Date': '',
        'Dictated on': '',
        'Trial ID': '',
        'Sex': '',
        'Birth': '',
        'Procedure': '',
        'Referring Physician': '',
        'Clinical History': '',
        'Clinical Information': '',
        'History': '',
        'Technique': '',
        'Comparison': '',
        'Findings or PET Findings': '',
        'Impression': ''
    }
    section_keys = {
        'Procedure': 'Procedure',
        'PROCEDURE': 'Procedure',
        'Referring Physician': 'Referring Physician',
        'REFERRING PHYSICIAN': 'Referring Physician',
        'Clinical History': 'Clinical History',
        'CLINICAL HISTORY': 'Clinical History',
        'Clinical Information': 'Clinical Information',
        'CLINICAL INFORMATION': 'Clinical Information',
        'History': 'History',
        'HISTORY': 'History',
        'Technique': 'Technique',
        'TECHNIQUE': 'Technique',
        'Comparison': 'Comparison',
        'COMPARISON': 'Comparison',
        'Findings': 'Findings or PET Findings',
        'FINDINGS': 'Findings or PET Findings',
        'PET Findings': 'Findings or PET Findings',
        'PET FINDINGS': 'Findings or PET Findings',
        'Impression': 'Impression',
        'IMPRESSION': 'Impression'
    }
    current_section = None

    text = clean_text(text)  # Clean headers and page numbers before parsing
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if line.startswith('Scan Date:'):
            data['Scan Date'] = format_date(line.split('Scan Date:')[1].split('Dictated on:')[0].strip())
            data['Dictated on'] = format_date(line.split('Dictated on:')[1].split('Trial ID:')[0].strip())
        elif line.startswith('Trial ID:'):
            data['Trial ID'] = line.split('Trial ID:')[1].split('Sex:')[0].strip()
            data['Sex'] = line.split('Sex:')[1].split('Birth:')[0].strip()
            birth_and_report = line.split('Birth:')[1]
            data['Birth'] = format_date(birth_and_report.strip())
        
        # Handle sections, considering case insensitivity
        for sec in section_keys:
            if line.startswith(sec):
                current_section = section_keys[sec]
                content_start = line.find(':') + 1 if ':' in line else len(line)
                data[current_section] = line[content_start:].strip()
                break

        if current_section and not any(line.startswith(sec) for sec in section_keys):
            data[current_section] += ' ' + line.strip()

    return data

# List to store data from all PDFs
all_data = []

# Process each PDF in the folder
for pdf_file in os.listdir(pdf_folder):
    if pdf_file.endswith('.pdf'):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        text = extract_text_from_pdf(pdf_path)
        report_data = parse_information(text)
        all_data.append(report_data)

# Create a DataFrame and write it to an Excel file
df = pd.DataFrame(all_data)
df = df[['Scan Date', 'Dictated on', 'Trial ID', 'Sex', 'Birth', 'Procedure', 'Referring Physician', 'Clinical History', 
         'Clinical Information', 'History', 'Technique', 'Comparison', 'Findings or PET Findings', 'Impression']]

df.to_excel(output_file, index=False)

print('Data extraction complete. Output saved to:', output_file)
