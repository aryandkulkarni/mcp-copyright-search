"""
Copyright Database Search Module

This module provides functionality to search the U.S. Copyright Office's 
public registration database and format the results.
"""

import sys
import requests

def format_copyright_data(data):
    """Format copyright search results into a more readable format."""
    if not data:
        return "No data to format."
    
    # Extract metadata
    metadata = data.get('metadata', {})
    records = data.get('data', [])
    
    # Format metadata summary
    output = []
    output.append("=" * 60)
    output.append("COPYRIGHT SEARCH RESULTS")
    output.append("=" * 60)
    output.append(f"Search took: {metadata.get('took_ms', 'N/A')} ms")
    output.append(f"Total hits: {metadata.get('hit_count', 'N/A')}")
    output.append(f"Query: {metadata.get('query', 'N/A')}")
    output.append("")
    
    # Format each record
    for i, record in enumerate(records, 1):
        hit = record.get('hit', {})
        score = record.get('score', 'N/A')
        
        output.append(f"RECORD {i}")
        output.append("-" * 30)
        output.append(f"Relevance Score: {score}")
        
        # Title
        title = hit.get('title_concatenated', 'N/A')
        if title != 'N/A':
            # Clean up title formatting
            title = title.replace('/', ' / ')
        output.append(f"Title: {title}")
        
        # Registration info
        reg_number = hit.get('registration_number', 'N/A')
        reg_date = hit.get('registration_date', 'N/A')
        reg_class = hit.get('registration_class', 'N/A')
        output.append(f"Registration: {reg_number} (Class: {reg_class})")
        output.append(f"Registration Date: {reg_date}")
        
        # Type of work
        work_type = hit.get('type_of_work_to_english', hit.get('type_of_work', 'N/A'))
        output.append(f"Type of Work: {work_type}")
        
        # Authors/Claimants
        display_names = hit.get('display_names', {})
        
        # Authors
        authors = display_names.get('persons', [])
        if authors:
            author_names = [author.get('name', 'Unknown') for author in authors if 'author' in author.get('roles', [])]
            if author_names:
                output.append(f"Authors: {', '.join(author_names)}")
        
        # Organizations
        orgs = display_names.get('organizations', [])
        if orgs:
            org_names = [org.get('name', 'Unknown') for org in orgs]
            output.append(f"Organizations: {', '.join(org_names)}")
        
        # Publication info
        pub_date = hit.get('first_published_date', hit.get('publication_date', 'N/A'))
        if pub_date != 'N/A':
            output.append(f"Publication Date: {pub_date}")
        
        # Status
        status = hit.get('registration_status', 'N/A')
        output.append(f"Status: {status}")
        
        # Creation date
        creation_date = hit.get('date_creation_date', 'N/A')
        if creation_date != 'N/A':
            output.append(f"Creation Date: {creation_date}")
        
        output.append("")
    
    return "\n".join(output)


    
def search_book(title, page_number=1, records_per_page=10, field_type='title'):
    url = "https://api.publicrecords.copyright.gov/search_service_external/simple_search_dsl"

    params = {
        "page_number": page_number,
        "records_per_page": records_per_page,
        "query": title,
        "field_type": field_type,
        "model": "",  # seems required by frontend, even if empty
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # raise error if not status 200

    data = response.json()
    records = data.get('data', [])

    formatted_results = format_copyright_data(data)
    
    return formatted_results

if __name__ == "__main__":
    print(search_book("Harry Potter and the Prisoner of Azkaban"))
    