import sys
import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Add the pii-redactor directory to the Python path so we can import its modules
PII_REDACTOR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "pii-redactor"))
sys.path.append(PII_REDACTOR_DIR)

from main import process_document

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def cleanup_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"Failed to cleanup {path}: {e}")

@app.post("/api/redact")
async def redact_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # Create temporary files for input and output
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_in:
        shutil.copyfileobj(file.file, temp_in)
        temp_in_path = temp_in.name
        
    temp_out_path = temp_in_path.replace(".docx", "_redacted.docx")
    mapping_path = temp_in_path.replace(".docx", "_mapping.json")

    try:
        # Run the PII redaction pipeline
        process_document(temp_in_path, temp_out_path, mapping_path)
        
        # Schedule cleanup of the temporary files after the response is sent
        background_tasks.add_task(cleanup_file, temp_in_path)
        background_tasks.add_task(cleanup_file, temp_out_path)
        background_tasks.add_task(cleanup_file, mapping_path)
        
        return FileResponse(
            path=temp_out_path,
            filename=f"redacted_{file.filename}",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        cleanup_file(temp_in_path)
        cleanup_file(temp_out_path)
        cleanup_file(mapping_path)
        return {"error": str(e)}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
