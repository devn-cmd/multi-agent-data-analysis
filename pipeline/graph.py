from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
import pandas as pd
from agents.cleaner_agent import cleaner_agent
from agents.analyst_agent import analyst_agent
from agents.reporter_agent import reporter_agent

class PipelineState(TypedDict):
    raw_df: pd.DataFrame
    clean_df: pd.DataFrame
    cleaning_summary: str
    findings: str
    analysis_code: str
    final_report: str
    source: Optional[str]       # "drive", "slack", or "upload"
    triggered_by: Optional[str] # filename or user

def build_pipeline():
    graph = StateGraph(PipelineState)
    graph.add_node("cleaner", cleaner_agent)
    graph.add_node("analyst", analyst_agent)
    graph.add_node("reporter", reporter_agent)
    graph.set_entry_point("cleaner")
    graph.add_edge("cleaner", "analyst")
    graph.add_edge("analyst", "reporter")
    graph.add_edge("reporter", END)
    return graph.compile()

pipeline = build_pipeline()

def run_pipeline_from_df(df: pd.DataFrame, source="upload", triggered_by="manual") -> dict:
    """Run pipeline from any DataFrame source."""
    return pipeline.invoke({
        "raw_df": df,
        "source": source,
        "triggered_by": triggered_by
    })

def run_pipeline_from_file(csv_path: str) -> str:
    df = pd.read_csv(csv_path)
    result = run_pipeline_from_df(df, source="local")
    return result["final_report"]