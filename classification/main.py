import shutil
from fastapi import FastAPI, UploadFile
from fastapi.responses import HTMLResponse
from standard_OCR.OCR import OCR



def extract_text(file,ocr_backend):
    ocr = OCR(ocr=ocr_backend)
    raw_text = ocr.get_text(file)
    return raw_text

@app.post("/", response_class=HTMLResponse)
async def classify_page(file: UploadFile, temp_file_path="./temp.pdf"):
    pass