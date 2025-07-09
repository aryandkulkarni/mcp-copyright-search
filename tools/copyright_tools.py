"""
Copyright MCP Server Tools

Provides MCP tools for searching the U.S. Copyright Office database.
"""

import sys
from server import mcp
from .search_book import search_book


@mcp.tool()
def search_book_by_title(title: str) -> dict:
    """
    Search the Copyright Public Records System with the title of a book
    
    Args:
        title: Name of a book to be searched
        
    Returns:
        A dict containing the search results
    """
    try:
        text = search_book(title)
        print(f"DEBUG: Raw text result: {repr(text)}", file=sys.stderr)
        
        # Test 2: Return the MCP format as dict (not JSON string)
        return format_mcp_response(text)
        
    except Exception as e:
        error_msg = f"Error searching for book: {str(e)}"
        print(f"DEBUG: Error occurred: {error_msg}", file=sys.stderr)
        return format_mcp_error(error_msg)

def format_mcp_response(text: str, is_error: bool = False) -> dict:
    """
    Converts a text response string into the proper MCP response format
    
    Args:
        text (str): The response text to format
        is_error (bool): Whether this is an error response (default: False)
    
    Returns:
        dict: Formatted MCP response object
    """
    response = {
        "content": [
            {
                "type": "text",
                "text": text
            }
        ]
    }
    
    if is_error:
        response["isError"] = True
    
    return response


def format_mcp_success(text: str) -> dict:
    """
    Convenience function for success responses
    
    Args:
        text (str): The success response text
    
    Returns:
        dict: Formatted MCP success response
    """
    return format_mcp_response(text, is_error=False)


def format_mcp_error(text: str) -> dict:
    """
    Convenience function for error responses
    
    Args:
        text (str): The error message
    
    Returns:
        dict: Formatted MCP error response
    """
    return format_mcp_response(text, is_error=True)