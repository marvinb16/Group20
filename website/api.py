import json
import re
import requests

from .models import FarmersMarket
from . import db

api_response = None

def extract_data_structure(response):
    # Pattern Recognition
    response = str(response)
    start_index = response.find('{"data":')

    if start_index != -1:
        # Extract data at the index of found data
        data_string = response[start_index:]
        #print("DEBUG DATA PULL " + data_string)

        # Attempt to parse the extracted data as JSON
        try:
            json_data = json.loads(data_string)
            #print("EXTRACTED JSON:", json_data)
            #print(type(json_data))

            if 'data' in json_data:
                extracted_data = json_data
                #print("EXTRACTED JSON:", extracted_data)
                #print(type(extracted_data))
                return extracted_data['data']
            else:
                print("No 'data' found in JSON")
                return None
        except json.JSONDecodeError:
            print("Invalid JSON data")
            return None
    else:
        print("String not found")
        return None

def format_market_data(market_data_list):
    # Formats to regular format because its in a weird text format not json
    formatted_data = {
        "data": []
    }
    for item in market_data_list:
        formatted_item = {
            "listing_id": item.get('listing_id'),
            "listing_name": item.get('listing_name'),
            "listing_desc": item.get('listing_desc'),
            "contact_name": item.get('contact_name'),
            "contact_email": item.get('contact_email'),
            "contact_phone": item.get('contact_phone'),
            "media_website": item.get('media_website'),
            "media_facebook": item.get('media_facebook'),
            "media_twitter": item.get('media_twitter'),
            "media_instagram": item.get('media_instagram'),
            "media_pinterest": item.get('media_pinterest'),
            "media_youtube": item.get('media_youtube'),
            "media_blog": item.get('media_blog'),
            "location_address": item.get('location_address'),
            "location_state": item.get('location_state'),
            "location_city": item.get('location_city'),
            "location_street": item.get('location_street'),
            "location_zipcode": item.get('location_zipcode'),
        }
        formatted_data["data"].append(formatted_item)
    return formatted_data

#returns the json structure
def fetch_farmers_market_data(zipcode, radius):
    global api_response
    apikey = 'tlnUddS4mT'
    apiUrl = f'https://www.usdalocalfoodportal.com/api/farmersmarket/?apikey={apikey}&zip={zipcode}&radius={radius}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
    }
    #print(apiUrl)

    try:
        response = requests.get(apiUrl, headers=headers)
        response.raise_for_status()

        try:
            api_response = response.json()
            if 'data' in api_response:
                return api_response
            else:
                print('No data found in the response:', api_response)
                return None
        except json.JSONDecodeError as e:
            print('Invalid JSON response:', str(e))
            # Handle the invalid JSON response here
            modified_response = extract_data_structure(response.text)
            if modified_response:
                api_response = format_market_data(modified_response)
                return api_response if modified_response else None
            return None
    except requests.exceptions.RequestException as e:
        print('Error fetching data:', str(e))
        # Handle the error and check if 'data' exists in the error response
        error_response = response.text if 'response' in locals() else None
        if error_response and 'data' in error_response:
            modified_response = extract_data_structure(error_response)
            if modified_response:
                api_response = format_market_data(modified_response)
                return api_response
        return None

#Getter for api call
def get_latest_api_call():
    return api_response

def get_market_data(listing_id):
    # Try to fetch market data from the database
    market_data = FarmersMarket.query.filter_by(listing_id=listing_id).first()

    if market_data is None:
        # Fetch market data from the API if not found in the database
        #print(api_response)

        api_data = get_market_data_from_api(api_response, listing_id)
        if api_data:
            # Create or update the market in the database
            market_data = create_or_update_market(api_data)

    return market_data

def create_or_update_market(market_data_list):
    # Ensure market_data_list is a list
    if not isinstance(market_data_list, list):
        market_data_list = [market_data_list]  # Convert to a list if it's a single entry

    updated_markets = []

    for market_data in market_data_list:
        # Millions of data format checks because for some reason it's all in different structures.
        if isinstance(market_data, dict):
            # If market_data is a dictionary
            listing_id = market_data.get('listing_id')
        elif isinstance(market_data, FarmersMarket):
            # If market_data is a FarmersMarket object
            listing_id = market_data.listing_id
        else:
            print("Error: Unsupported market_data type")
            continue

        if not listing_id:
            print("Error: 'listing_id' not found in market_data")
            continue

        # Check if the market already exists
        market = FarmersMarket.query.get(listing_id)

        if not market:
            # Create a new market
            market = FarmersMarket(**market_data)  # Pass the attributes directly
            db.session.add(market)
        else:
            # Update the existing market
            for key, value in market_data.items():
                setattr(market, key, value)

        updated_markets.append(market)

    db.session.commit()

    return updated_markets



def get_market_data_from_api(api_response, listing_id):
    #print ("DEBUG", api_response)
    if api_response is None or 'data' not in api_response:
        print("Error: 'data' key not found in API response")
        return None

    market_data_list = api_response['data']
    market_data = next((item for item in market_data_list if item.get('listing_id') == listing_id), None)

    if market_data is None:
        print(f"Error: Market data not found for listing_id {listing_id}")
        return None

    return market_data
