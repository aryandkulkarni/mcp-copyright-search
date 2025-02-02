#!/usr/bin/env python3

import asyncio
import json
from typing import Any, Sequence, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

from mcp.server import Server, NotificationOptions
from mcp.server.models import (
    InitializeResult,
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)
from mcp.server.resources import read_resource
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListResourcesResult,
    ListToolsResult,
    ReadResourceResult,
    TextResourceContents,
    ImageResourceContents,
)

# Server configuration
SERVER_NAME = "copyright-records-server"
SERVER_VERSION = "0.1.0"

# Base URLs for the copyright systems
CPRS_BASE_URL = "https://publicrecords.copyright.gov"

class CopyrightSearcher:
    def __init__(self):
        self.session = requests.Session()
        # Set a reasonable user agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_cprs(self, title: str, author: Optional[str] = None) -> dict:
        """
        Search the Copyright Public Records System Pilot
        
        Note: This is a template implementation. You'll need to:
        1. Visit https://publicrecords.copyright.gov in your browser
        2. Inspect the search form to find the actual field names and endpoints
        3. Update the search_url and form_data accordingly
        """
        try:
            # First, get the search page to understand the form structure
            search_url = f"{CPRS_BASE_URL}/search"  # This might be different
            
            # Get the search page
            response = self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # TODO: Inspect the actual form structure and update these field names
            # Common field names might be: title, author, work_title, creator, etc.
            form_data = {
                'title': title,  # Update with actual field name
                'q': title,      # Alternative common field name
                'search_type': 'advanced',  # Might be needed
            }
            
            # Add author if provided  
            if author:
                form_data['author'] = author  # Update with actual field name
                form_data['creator'] = author  # Alternative field name
            
            # Find the form action URL (this is a guess - needs to be verified)
            form = soup.find('form')
            if form:
                action = form.get('action', '/search')
                search_endpoint = urljoin(CPRS_BASE_URL, action)
            else:
                search_endpoint = f"{CPRS_BASE_URL}/search"
            
            # Submit the search
            search_response = self.session.post(search_endpoint, data=form_data)
            search_response.raise_for_status()
            
            # Parse the results
            results = self._parse_search_results(search_response.text)
            
            return {
                'success': True,
                'query': {'title': title, 'author': author},
                'results': results,
                'total_results': len(results)
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request failed: {str(e)}',
                'query': {'title': title, 'author': author}
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'query': {'title': title, 'author': author}
            }
    
    def _parse_search_results(self, html_content: str) -> list:
        """
        Parse search results from the HTML response
        
        Note: This needs to be customized based on the actual HTML structure
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # TODO: Update these selectors based on the actual HTML structure
        # Common patterns might be: .result-item, .search-result, tr (for tables), etc.
        result_items = soup.find_all('div', class_='result')  # Placeholder selector
        
        if not result_items:
            # Try alternative selectors
            result_items = soup.find_all('tr')  # If results are in a table
            
        for item in result_items:
            try:
                # Extract common fields - update selectors as needed
                title = self._extract_text(item, ['.title', 'h3', 'h4', '.work-title'])
                author = self._extract_text(item, ['.author', '.creator', '.claimant'])
                reg_number = self._extract_text(item, ['.registration-number', '.reg-num'])
                reg_date = self._extract_text(item, ['.registration-date', '.reg-date'])
                
                if title:  # Only add if we found at least a title
                    results.append({
                        'title': title,
                        'author': author,
                        'registration_number': reg_number,
                        'registration_date': reg_date,
                        'raw_html': str(item)  # For debugging
                    })
            except Exception as e:
                # Continue processing other results if one fails
                continue
        
        return results
    
    def _extract_text(self, element, selectors: list) -> Optional[str]:
        """Helper method to try multiple selectors and return the first match"""
        for selector in selectors:
            found = element.select_one(selector)
            if found:
                return found.get_text(strip=True)
        return None

# Initialize the searcher
searcher = CopyrightSearcher()

# Create the MCP server
app = Server(SERVER_NAME)

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_copyright_records",
            description="Search the US Copyright Office Public Records System for copyright registrations by title, with optional author filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the work to search for"
                    },
                    "author": {
                        "type": "string",
                        "description": "Optional: Author/creator name to filter results",
                        "optional": True
                    }
                },
                "required": ["title"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    if name == "search_copyright_records":
        title = arguments.get("title", "")
        author = arguments.get("author")
        
        if not title:
            return [TextContent(
                type="text",
                text="Error: Title is required for copyright search"
            )]
        
        # Perform the search
        results = searcher.search_cprs(title, author)
        
        # Format the response
        if results['success']:
            response_text = f"# Copyright Records Search Results\n\n"
            response_text += f"**Query:** Title: '{title}'"
            if author:
                response_text += f", Author: '{author}'"
            response_text += f"\n**Total Results:** {results['total_results']}\n\n"
            
            if results['results']:
                for i, result in enumerate(results['results'], 1):
                    response_text += f"## Result {i}\n"
                    response_text += f"**Title:** {result['title']}\n"
                    if result['author']:
                        response_text += f"**Author:** {result['author']}\n"
                    if result['registration_number']:
                        response_text += f"**Registration Number:** {result['registration_number']}\n"
                    if result['registration_date']:
                        response_text += f"**Registration Date:** {result['registration_date']}\n"
                    response_text += "\n---\n\n"
            else:
                response_text += "No results found for this search.\n"
        else:
            response_text = f"# Search Failed\n\n"
            response_text += f"**Error:** {results['error']}\n"
            response_text += f"**Query:** Title: '{title}'"
            if author:
                response_text += f", Author: '{author}'"
            
        return [TextContent(type="text", text=response_text)]
    
    else:
        return [TextContent(
            type="text", 
            text=f"Unknown tool: {name}"
        )]

async def main():
    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializeResult(
                serverName=SERVER_NAME,
                serverVersion=SERVER_VERSION,
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())