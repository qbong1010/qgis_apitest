import requests
import urllib.parse

def fetch_building_info(service_key, sigungu_cd, bjdong_cd, plat_gb_cd, bun, ji, rows=1, page=1, response_type="json"):
    """
    Fetch building registry information based on parameters from the OpenAPI.

    :param service_key: Decoded service key from the public data portal
    :param sigungu_cd: City/district code
    :param bjdong_cd: Legal dong code
    :param plat_gb_cd: Land classification code (0: land, 1: mountain, etc.)
    :param bun: Main lot number
    :param ji: Sub lot number
    :param rows: Number of rows per page
    :param page: Page number
    :param response_type: Response format (json or xml)
    :return: API response in JSON format
    """
    # Base URL for the API
    base_url = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo"

    # API parameters
    params = {
        "serviceKey": service_key,
        "sigunguCd": sigungu_cd,
        "bjdongCd": bjdong_cd,
        "platGbCd": plat_gb_cd,
        "bun": bun,
        "ji": ji,
        "numOfRows": rows,
        "pageNo": page,
        "_type": response_type
    }

    try:
        # Send a GET request
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        if response_type == "json":
            # Print raw response for debugging
            print("Raw response:", response.text)
            
            # Check if response is empty
            if not response.text.strip():
                return {"error": "Empty response received from server"}
                
            try:
                return response.json()
            except ValueError as json_err:
                return {"error": f"Failed to parse JSON response: {json_err}", "raw_response": response.text}
        else:
            return response.text
    except requests.exceptions.ConnectionError:
        return {"error": "Connection error occurred. Please check your network or the API server."}
    except requests.exceptions.Timeout:
        return {"error": "The request timed out. Please try again later."}
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred: {e}"}

# Example usage
if __name__ == "__main__":
    # Decode the service key first
    service_key = urllib.parse.unquote("Lvn%2FX9ciaH3OcErj46QABbDpndkMA%2FBR6ZJmLMlTOO1No1vGocwgMhcp%2BVKl%2BShi8et1lD%2BVhhVAdQNi%2BtkKGw%3D%3D")

    # Parameters based on the provided URL example
    sigungu_cd = "11680"
    bjdong_cd = "10300"
    plat_gb_cd = "0"
    bun = "0012"
    ji = "0000"

    # Fetch building information
    building_info = fetch_building_info(service_key, sigungu_cd, bjdong_cd, plat_gb_cd, bun, ji, rows=10, page=1)

    # Print the result
    print(building_info)
