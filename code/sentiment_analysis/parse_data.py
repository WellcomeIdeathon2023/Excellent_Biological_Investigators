import pandas as pd
from geograpy.locator import Locator
from geograpy.extraction import Extractor

def get_location(text):
    city = "NA"
    country = "NA"
    e = Extractor(text=text)
    e.split()
    loc = Locator.getInstance()
    places = loc.normalizePlaces(e.places)

    for location in places:
        parse_country = loc.getCountry(location)
        if parse_country != None:
            country = parse_country.name
            break

    combined_loc = loc.locateCity(places)

    # ensure countries match
    if combined_loc != None:
        if country != "NA":
            if country == combined_loc.country.name:
                city = combined_loc.name
        else:
            country = combined_loc.country.name
            city = combined_loc.name

    return country, city

def extract_clean_address(address, geolocator, geocode):
    try:
        location = geocode(address)
        location = geolocator.reverse([location.latitude, location.longitude])
        return location.raw['address']['country'], location.raw['address']['city']
    except:
        return ''

def read_infile(infile):
    df = pd.read_csv(infile, delimiter=",", header=0)
    df['text'] = df['text'].replace('\n', ' ', regex=True)

    df = df.where(pd.notnull(df), None)

    return df


