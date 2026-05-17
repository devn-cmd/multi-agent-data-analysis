# Multi-Agent Data Analysis Pipeline

> AI-powered data analysis pipeline using multiple agents, LangGraph orchestration, Docker, and local LLMs.

## 🚧 Current Status
Phase 1 Completed — Initial Project Setup

This project is currently in the foundational setup stage before Google Drive and Slack MCP integrations.

The core folder architecture, development environment, and pipeline structure have been initialized successfully.

---

## 📌 Project Goal

Build an end-to-end autonomous data analysis system where multiple AI agents:

1. Fetch CSV data
2. Clean and preprocess datasets
3. Analyze trends and anomalies
4. Generate business reports
5. Deliver reports automatically through external integrations

---

## 🧠 Planned Architecture

```text
Google Drive / Slack
        ↓
   MCP Connectors
        ↓
Cleaner Agent
        ↓
Analyst Agent
        ↓
Reporter Agent
        ↓
Slack / Drive Report Delivery
```

---

## ⚙️ Tech Stack

- Python 3.11
- LangGraph
- Ollama
- Docker & Docker Compose
- FastAPI
- Streamlit
- Pandas
- MCP SDK
- Google Drive API
- Slack SDK

---

## ✅ Phase 1 Progress

Completed:

- Project folder structure
- Python virtual environment setup
- Docker setup
- Ollama local LLM setup
- Initial dependency installation
- Agent architecture planning
- Pipeline module structure

In Progress:

- Google Drive MCP integration
- Slack integration
- LangGraph workflow implementation

---

## 📂 Project Structure

```text
multi-agent-data-analysis/
├── agents/
├── pipeline/
├── api/
├── ui/
├── mcp/
├── data/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 🎯 Upcoming Features

- Autonomous CSV fetching from Google Drive
- Slack-triggered analysis
- Multi-agent orchestration using LangGraph
- Automated report generation
- Claude Desktop MCP support
- Streamlit dashboard

---

## 🚀 Future Vision

The final system will allow users to trigger data analysis directly from Slack or Claude Desktop, automatically process datasets through AI agents, and receive summarized business reports without manual intervention.

---

## 🛠️ Development Roadmap

| Phase | Status |
|---|---|
| Environment Setup | ✅ Completed |
| Agent Development | 🔄 In Progress |
| Dockerized API | ⏳ Planned |
| MCP Integrations | ⏳ Planned |
| UI Dashboard | ⏳ Planned |

---

## 📖 Reference Guide

Project implementation is based on the development guide in:

`multi_agent_pipeline_guide_linux.md`

:contentReference[oaicite:1]{index=1}

---

## 👨‍💻 Author

Devadeth N
