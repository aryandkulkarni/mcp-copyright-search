import requests

def search_copyright_records(query, page_number=1, records_per_page=10, sort_order='asc', field_type='keyword'):
    url = "https://api.publicrecords.copyright.gov/search_service_external/simple_search_dsl"

    params = {
        "page_number": page_number,
        "query": query,
        "field_type": field_type,
        "records_per_page": records_per_page,
        "sort_order": sort_order,
        "model": ""  # seems required by frontend, even if empty
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # raise error if not status 200

        data = response.json()
        print("Search results:")
        print(data)

    except requests.RequestException as e:
        print("Request failed:", e)
    except ValueError:
        print("Failed to parse JSON. Response content:")
        print(response.text[:1000])

if __name__ == "__main__":
    search_copyright_records("Star Wars")
