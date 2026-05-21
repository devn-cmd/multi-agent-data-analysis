from langchain_ollama import OllamaLLM
import pandas as pd
import io

#llm=OllamaLLM(model="qwen3:4b-q4_K_M")
import os
llm = OllamaLLM(
    model=os.getenv("OLLAMA_MODEL", "qwen3:4b-q4_K_M"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)
def cleaner_agent(state:dict) -> dict:
    df= state["raw_df"]

    #fix common issues
    df=df.drop_duplicates()
    df=df.dropna(thresh=len(df.columns)*0.5)# drop rows >50% empty

    for col in df.select_dtypes(include="number").columns:
        df[col]=df[col].fillna(df[col].median())# fill numeric with median

    for col in df.select_dtypes(include="object").columns:
        df[col]=df[col].fillna("Unknown")# fill categorical with "Unknown"  
    
    # ask LLm  to summarize what fixed

    summary_prompt=f"""
    I cleaned a dataset with {state['raw_df'].shape[0]} rows and {state['raw_df'].shape[1]} columns.
    Issues found and fixed:
    - Duplicates removed: {state['raw_df'].duplicated().sum()}
    - Missing values filled: {state['raw_df'].isnull().sum().sum()}
    Write a 2-sentence cleaning summary for a business report.
    """

    cleaning_summary=llm.invoke(summary_prompt)

    return {**state, "clean_df": df, "cleaning_summary": cleaning_summary}
