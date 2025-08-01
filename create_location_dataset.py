
import requests
import wikipedia
import json

# Configuration
GEONAMES_USERNAME = "rajghosh"  # Replace with your GeoNames username


def get_countries():
    """Fetches a list of countries from the World Bank API."""
    url = "http://api.worldbank.org/v2/country?format=json&per_page=300"
    response = requests.get(url)
    data = response.json()
    countries = []
    for country in data[1]:
        if country['region']['value'] != 'Aggregates':
            countries.append({
                "name": country['name'],
                "iso3": country['id'],
                "iso2": country['iso2Code'],
                "income_level": country['incomeLevel']['value'],
                "region": country['region']['value']
            })
    return countries

def get_cities(country_iso2, geonames_username):
    """Fetches the top 3 most populous cities for a given country."""
    url = f"http://api.geonames.org/searchJSON?country={country_iso2}&featureClass=P&orderBy=population&maxRows=3&username={geonames_username}"
    try:
        response = requests.get(url)
        data = response.json()
        cities = []
        if 'geonames' in data:
            for city in data['geonames']:
                cities.append({
                    "name": city['name'],
                    "country": city['countryName'],
                    "region": city.get('adminName1', ''),
                    "population": city.get('population', 0),
                    "lat": city.get('lat', 0),
                    "lng": city.get('lng', 0),
                    "timezone": city.get('timezone', {}).get('timeZoneId', '')
                })
        return cities
    except Exception as e:
        try:
            print(f"Error fetching cities for {country_iso2}: {e}")
        except UnicodeEncodeError:
            print(f"Error fetching cities for {country_iso2.encode('utf-8')}: {e}")
        return []

def get_wikipedia_summary(query):
    """Fetches a short Wikipedia summary for a given query."""
    try:
        return wikipedia.summary(query, sentences=3)
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"Disambiguation error for {query}: {e}")
        # Try a simpler query
        try:
            return wikipedia.summary(query.split(',')[0], sentences=3)
        except Exception as inner_e:
            print(f"Could not resolve disambiguation for {query}: {inner_e}")
            return ""
    except Exception as e:
        print(f"Error fetching Wikipedia summary for {query}: {e}")
        return ""

def main():
    """Main function to create the location dataset."""
    if GEONAMES_USERNAME == "YOUR_GEONAMES_USERNAME":
        geonames_username = input("Please enter your GeoNames username: ")
        if not geonames_username:
            print("GeoNames username is required to proceed.")
            return
    else:
        geonames_username = GEONAMES_USERNAME

    countries = get_countries()
    all_locations = []

    for country in countries:
        print(f"Processing {country['name']}...")
        cities = get_cities(country['iso2'], GEONAMES_USERNAME)
        for city in cities:
            # Add development level
            if country['income_level'] in ['High income', 'Upper middle income']:
                development_level = 'developed'
            else:
                development_level = 'developing'

            # Get Wikipedia summary
            wiki_query = f"{city['name']}, {city['country']}"
            summary = get_wikipedia_summary(wiki_query)

            all_locations.append({
                **city,
                "development_level": development_level,
                "region": country['region'],
                "wikipedia_summary": summary
            })

    with open('locations.json', 'w') as f:
        json.dump(all_locations, f, indent=2)

    print(f"Successfully created locations.json with {len(all_locations)} locations.")

if __name__ == "__main__":
    main()
