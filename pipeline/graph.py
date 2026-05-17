from langgraph.graph import StateGraph, END
from typing import TypedDict
import pandas as pd
from agents.cleaner_agent import cleaner_agent
from agents.analyst_agent import analyst_agent
from agents.reporter_agent import reporter_agent


class PipelineState(TypedDict):
    raw_df:pd.DataFrame
    clean_df:pd.DataFrame
    cleaning_summary:str
    findings:str
    analysis_code:str
    final_report:str

def build_pipeline():
    graph=StateGraph(PipelineState)
    graph.add_node("cleaner", cleaner_agent)
    graph.add_node("analyst", analyst_agent)
    graph.add_node("reporter", reporter_agent)


    graph.set_entry_point("cleaner")
    graph.add_edge("cleaner","analyst")
    graph.add_edge("analyst","reporter")
    graph.add_edge("reporter",END)

    return graph.compile()

pipeline=build_pipeline()

def run_pipeline(csv_path: str) -> str:
    df=pd.read_csv(csv_path)
    result=pipeline.invoke({"raw_df": df})
    return result["final_report"]
