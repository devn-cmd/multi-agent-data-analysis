from langchain_ollama import OllamaLLM

llm=OllamaLLM(model="qwen3:4b-q4_K_M")

def reporter_agent(state: dict) -> dict:
    report_prompt=f"""
    You are a data analyst writing a bussiness report.

    CLEANING SUMMARY:
    {state['cleaning_summary']}

    ANALYSIS FINDINGS:
    {state['findings']}

    Write a structured report with these sections:
    1. Executive Summary (3 sentences)
    2. Key Findings (3-5 bullet points)
    3. Recommendations (2-3 actionable suggestions)
    4. Next Steps

    Keep it professional and concise. No technical jargon.
    """

    report=llm.invoke(report_prompt)

    return {**state, "final_report": report}