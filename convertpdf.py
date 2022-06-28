from pdf2docx import parse
from typing import Tuple
import os

def CreateAndDelete(dir_path):

    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
    count = 0
    for path in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, path)):
            count +=1
    
    if count > 5:
        for path in os.listdir(dir_path):
            os.remove(os.path.join(dir_path, path))

def convert_pdf2docx(input_file: str, output_file: str, pages: Tuple = None):
    """Converts pdf to docx"""
    if pages:
        pages = [int(i) for i in list(pages) if i.isnumeric()]
    result = parse(pdf_file=input_file,
                   docx_with_path=output_file, pages=pages)
    summary = {
        "File": input_file, "Pages": str(pages), "Output File": output_file
    }
    return result