"""
Copyright MCP Server Main Entry Point

This is the main entry point for the Copyright MCP Server that provides
tools for searching the U.S. Copyright Office's public registration database.
"""

import sys
import os
from server import mcp
import tools.copyright_tools

# Add debugging output to stderr so it appears in Claude's logs
print("Copyright MCP Server starting...", file=sys.stderr)
print(f"Current working directory: {os.getcwd()}", file=sys.stderr)
print(f"Python path: {sys.path}", file=sys.stderr)
print("Copyright tools imported successfully", file=sys.stderr)

# Entry point to run the server
if __name__ == "__main__":
    print("Running Copyright MCP server...", file=sys.stderr)
    mcp.run()