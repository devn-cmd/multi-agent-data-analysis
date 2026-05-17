import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from pipeline.graph import run_pipeline_from_df, run_pipeline_from_file
from mcp.gdrive_connector import fetch_csv_from_drive, save_report_to_drive
from mcp.slack_connector import post_report_to_slack

app = Server("data-pipeline-mcp")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="analyze_local_csv",
            description="Analyze a CSV file from a local path using the multi-agent pipeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Local path to the CSV file"}
                },
                "required": ["file_path"]
            }
        ),
        types.Tool(
            name="analyze_drive_csv",
            description="Fetch a CSV from Google Drive and analyze it",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_name": {"type": "string", "description": "Name of the CSV file in Drive"},
                    "post_to_slack": {"type": "boolean", "description": "Post report to Slack after analysis"}
                },
                "required": ["file_name"]
            }
        ),
        types.Tool(
            name="run_slack_triggered_analysis",
            description="Check Slack for an 'analyze' message, fetch the mentioned CSV from Drive, run pipeline, post report back",
            inputSchema={"type": "object", "properties": {}}
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    if name == "analyze_local_csv":
        report = run_pipeline_from_file(arguments["file_path"])
        return [types.TextContent(type="text", text=report)]

    elif name == "analyze_drive_csv":
        file_name = arguments["file_name"]
        df = fetch_csv_from_drive(file_name)
        result = run_pipeline_from_df(df, source="drive", triggered_by=file_name)
        report = result["final_report"]

        drive_url = save_report_to_drive(report, f"report_{file_name}")

        if arguments.get("post_to_slack"):
            post_report_to_slack(report, triggered_by=file_name)

        return [types.TextContent(
            type="text",
            text=f"{report}\n\n---\nReport saved to Drive: {drive_url}"
        )]

    elif name == "run_slack_triggered_analysis":
        from mcp.slack_connector import get_latest_trigger_message, extract_filename_from_message, post_error_to_slack
        msg = get_latest_trigger_message()
        if not msg:
            return [types.TextContent(type="text", text="No 'analyze' trigger found in Slack.")]

        file_name = extract_filename_from_message(msg)
        if not file_name:
            return [types.TextContent(type="text", text="Trigger message found but no CSV filename detected.")]

        try:
            df = fetch_csv_from_drive(file_name)
            result = run_pipeline_from_df(df, source="slack", triggered_by=file_name)
            report = result["final_report"]
            post_report_to_slack(report, triggered_by=file_name)
            return [types.TextContent(type="text", text=f"Done. Report posted to Slack for '{file_name}'.")]
        except Exception as e:
            post_error_to_slack(str(e))
            return [types.TextContent(type="text", text=f"Pipeline failed: {e}")]

    return [types.TextContent(type="text", text="Unknown tool.")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())