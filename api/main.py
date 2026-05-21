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

@app.post("/trigger/telegram") # Renamed for clarity
async def telegram_trigger():
    """Called by Cline or a webhook to run the pipeline."""
    # FIXED: Updated function names to match your telegram_connector.py
    from ModelContextProtocol.telegram_connector import (
        get_latest_trigger_message, 
        extract_filename_from_message, 
        post_report_to_telegram, 
        post_error_to_telegram
    )
    from ModelContextProtocol.gdrive_connector import fetch_csv_from_drive

    # FIXED: Added 'await' because get_latest_trigger_message is an async function
    msg = await get_latest_trigger_message()
    if not msg:
        return JSONResponse({"status": "no_trigger"})

    file_name = extract_filename_from_message(msg)
    if not file_name:
        return JSONResponse({"status": "no_filename_in_message"})

    try:
            # 1. Fetch the data from Drive
            df = fetch_csv_from_drive(file_name)
            result = run_pipeline_from_df(df, source="telegram", triggered_by=file_name)
            
            # 2. Send the report to your Telegram
            await post_report_to_telegram(result["final_report"], triggered_by=file_name)
            
            # 3. Save the report back to Google Drive using your exact function
            from ModelContextProtocol.gdrive_connector import save_report_to_drive
            
            # Generate a clear report name (e.g., sample_Report.txt)
            report_filename = file_name.replace(".csv", "_Report.txt")
            
            # This calls your function, uploads the text, and grabs the shareable URL
            drive_url = save_report_to_drive(report=result["final_report"], report_name=report_filename)
            
            # 4. Return success including the new Drive link
            return JSONResponse({
                "status": "success", 
                "file": file_name, 
                "drive_url": drive_url
            })
            
    except Exception as e:
        await post_error_to_telegram(str(e))
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)