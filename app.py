import nltk
nltk.download('stopwords')
import os
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from pydparser import ResumeParser
import shutil
from fastapi.responses import FileResponse


app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload/")
async def upload_resumes(files: list[UploadFile] = File(...)):
    all_data = []

    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            data = ResumeParser(file_path).get_extracted_data()
            if data:
                data['file_name'] = file.filename
                all_data.append(data)
        except Exception as e:
            print(f"Error: {e}")

    df = pd.DataFrame(all_data)

    # Clean data
    if 'skills' in df.columns:
        df['skills'] = df['skills'].apply(
            lambda x: ', '.join(x) if isinstance(x, list) else x
        )

    df.fillna('', inplace=True)

    # Save Excel
    output_file = "parsed_resumes.xlsx"
    df.to_excel(output_file, index=False)

    return FileResponse(
    path=output_file,
    filename="parsed_resumes.xlsx",
    media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)
