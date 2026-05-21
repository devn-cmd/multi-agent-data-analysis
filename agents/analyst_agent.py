from langchain_ollama import OllamaLLM
import pandas as pd
import matplotlib
matplotlib.use('Agg')

#llm=OllamaLLM(model="qwen3:4b-q4_K_M")
import os
llm = OllamaLLM(
    model=os.getenv("OLLAMA_MODEL", "qwen3:4b-q4_K_M"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)
def analyst_agent(state: dict) ->dict:
    df=state["clean_df"]

    # generate basic stats
    stats=df.describe().to_string()
    columns=list(df.columns)

    code_prompt=f"""
    i have cleaned pandas DataFrame with columns"{columns}
    basic stats are:{stats}

    write python code (using only pandas) to:
    1. Find the top 3 trends or patterns
    2. Identify any anomalies or outliers
    3. Print findings as clear text
    Use df as the variable name. Output only code, no explanations.

    CRITICAL RULES:
    - Use df as the variable name. 
    - Output ONLY clean executable python code, no explanations.
    - DO NOT import matplotlib, seaborn, or any visualization libraries.
    - DO NOT attempt to plot graphs, charts, or render HTML. Text output only.
    """
    generated_code=llm.invoke(code_prompt)


    # Clean and execute the generated code
    clean_code = generated_code.replace("```python", "").replace("```", "").strip()

    exec_globals= {"df": df, "pd": pd}
    import io,sys
    captured=io.StringIO()
    sys.stdout=captured
    try:
        exec(clean_code,exec_globals)
    except Exception as e:
        print(f"Analysis note: {e}")
    finally:
        sys.stdout = sys.__stdout__

    findings=captured.getvalue()
    return {**state, "findings": findings, "analysis_code": clean_code}
