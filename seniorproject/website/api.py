import requests

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
