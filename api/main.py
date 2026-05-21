from fastapi import FastAPI, UploadFile, File
import pandas as pd
from fastapi.responses import JSONResponse
import io
from pipeline.graph import pipeline, run_pipeline_from_df

app = FastAPI(title="Multi-Agent Data Analysis Pipeline")

@app.get("/")
def health():
    return {"status": "running"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    df = pd.read_csv(io.StringIO(content.decode("utf-8")))
    result = pipeline.invoke({"raw_df": df})
    return JSONResponse(content=({
        "cleaning_summary": result["cleaning_summary"],
        "findings": result["findings"],
        "final_report": result["final_report"]
    }))

@app.post("/trigger/slack")
async def slack_trigger():
    """Called by Cline or a Slack webhook to run the pipeline."""
    from ModelContextProtocol.slack_connector import get_latest_trigger_message, extract_filename_from_message, post_report_to_slack, post_error_to_slack
    from ModelContextProtocol.gdrive_connector import fetch_csv_from_drive

    msg = get_latest_trigger_message()
    if not msg:
        return JSONResponse({"status": "no_trigger"})

    file_name = extract_filename_from_message(msg)
    if not file_name:
        return JSONResponse({"status": "no_filename_in_message"})

    try:
        df = fetch_csv_from_drive(file_name)
        result = run_pipeline_from_df(df, source="slack", triggered_by=file_name)
        post_report_to_slack(result["final_report"], triggered_by=file_name)
        return JSONResponse({"status": "success", "file": file_name})
    except Exception as e:
        post_error_to_slack(str(e))
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)