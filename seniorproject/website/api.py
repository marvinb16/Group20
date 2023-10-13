import requests

from .models import FarmersMarket
from . import db

api_response = None

#returns the json structure
def fetch_farmers_market_data(zipcode, radius):
    global api_response
    apikey = 'tlnUddS4mT'
    apiUrl = f'https://www.usdalocalfoodportal.com/api/farmersmarket/?apikey={apikey}&zip={zipcode}&radius={radius}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
    }

    try:
        response = requests.get(apiUrl, headers=headers)
        response.raise_for_status()
        api_response = response.json()
        print(api_response)

        return api_response
    except requests.exceptions.RequestException as e:
        print('Error fetching data:', str(e))
        return None


#Getter for api call
def get_latest_api_call():
    return api_response

def get_market_data(listing_id):
    # Fetch market data based on the listing_id from the provided data
    global api_response
    market_data = get_market_data_from_api(api_response, listing_id)
    return market_data
def create_or_update_market(market_data):
    listing_id = market_data.get('listing_id')

    # Check if the market already exists
    market = FarmersMarket.query.get(listing_id)

    if not market:
        # Create a new market
        market = FarmersMarket(**market_data)
        db.session.add(market)
    else:
        # Update the existing market
        for key, value in market_data.items():
            setattr(market, key, value)

    db.session.commit()

    return market

def get_market_data_from_api(api_response, listing_id):
    market_data_list = api_response.get('data', [])

    market_data = None
    for item in market_data_list:
        if item.get('listing_id') == listing_id:
            market_data = {
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
                "location_zipcode": item.get('location_zipcode')
            }
            break

    return market_data
