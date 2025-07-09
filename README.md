# Copyright MCP Server

An MCP (Model Context Protocol) server for searching and retrieving records from the U.S. Copyright Office's public registration database.

## Features

- Search copyright records by book title
- Retrieve detailed registration information
- Format results in a human-readable format

## Project Structure

```
copyright-mcp-server/
├── main.py              # Main entry point
├── server.py            # MCP server instance
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── tools/              # MCP tools package
    ├── __init__.py     # Package initialization
    ├── copyright_tools.py  # MCP tool definitions
    └── search_book.py  # Copyright database search logic
```

## Installation

1. Create a virtual environment:

```bash
python -m venv env
```

2. Activate the virtual environment:

```bash
# Windows
env\Scripts\activate
# macOS/Linux
source env/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the MCP server:

```bash
python main.py
```

## Tools

### search_book_by_title

Search the U.S. Copyright Office database for a book by title.

**Parameters:**

- `title` (string): The title of the book to search for

**Returns:**
Formatted search results including registration details, authors, publication dates, and more.
