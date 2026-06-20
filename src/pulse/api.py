import os
import glob
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pulse.pipeline import run_pulse_pipeline

app = FastAPI(title="Pulse Report API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow the Vite frontend to communicate
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/reports")
def get_reports():
    """
    Scans the data/reports directory, reads all JSON reports,
    and returns them in descending order of creation date.
    """
    pattern = "data/reports/*.json"
    files = glob.glob(pattern)
    
    reports = []
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
                # Ensure we add an ID to the report for frontend keys
                report_data["id"] = os.path.basename(file_path).replace(".json", "")
                reports.append(report_data)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
    # Sort reports by end_date descending
    reports.sort(key=lambda x: x.get("end_date", ""), reverse=True)
    return reports

@app.post("/api/reports/generate")
def generate_report():
    """
    Triggers an ad-hoc pipeline run using the current date as the end_date.
    """
    try:
        run_pulse_pipeline(product="groww", end_date_override=datetime.now())
        return {"status": "success", "message": "Report generated successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("pulse.api:app", host="0.0.0.0", port=8000, reload=True)
