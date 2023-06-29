import pandas as pd
from datetime import datetime
from sentiment_analysis import preprocess
import geograpy

def get_location(text):
    places = geograpy.get_place_context(text=text)
    return places

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

    #geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.5, max_retries=10)
    # df['parsed_location'] = df['user_location'].apply(geocode)
    # df['point'] = df['parsed_location'].apply(lambda loc: tuple(loc.point) if loc else None)

    #df.to_csv("vax_tweets_location.csv", index=False)

    #unique_addresses = pd.unique(df['user_location'])

    for index, row in df.iterrows():
        text = preprocess(row['text'])
        date_time = datetime.strptime(row['date'], '%d/%m/%Y %H:%M')

        messy_address = row['user_location']
        location = ("NA", "NA")
        if messy_address != "" and messy_address != None:
            parsed_location = get_location(row['user_location'])
            # get first inferred country and city
            if len(parsed_location.countries) > 0:
                country = parsed_location.countries[0]
                city = "NA"
                if country in parsed_location.country_cities:
                    city = parsed_location.country_cities[parsed_location.countries[0]][0]
                location = (country, city)


        #lat, long, point = row['point']

        #location = get_country(lat, long)

        # parse address

        #location = extract_clean_address(messy_address, geolocator, geocode)
        # if isinstance(messy_address, str):
        #     location = extract_clean_address(messy_address, geolocator, geocode)
        # else:
        #     location = None

        yield text, date_time, location