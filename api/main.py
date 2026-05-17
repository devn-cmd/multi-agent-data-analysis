from fastapi import FastAPI, UploadFile, File
import pandas as pd
from fastapi.responses import JSONResponse
import io
from pipeline.graph import pipeline


app=FastAPI(title="Multi-Agent Data Analysis Pipeline")

@app.get("/")
def health():
    return {"status": "running"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content=await file.read()
    df= pd.read_csv(io.StringIO(content.decode("utf-8")))

    result=pipeline.invoke({"raw_df": df})

    return JSONResponse(content=({
        "cleaning_summary": result["cleaning_summary"],
        "findings": result["findings"], 
        "final_report": result["final_report"]
        }))


