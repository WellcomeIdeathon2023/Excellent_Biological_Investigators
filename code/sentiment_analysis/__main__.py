from parse_data import read_infile, get_location
from sentiment_analysis import *
from datetime import datetime
from shared_memory import *
from tqdm import *
import argparse
import pandas as pd
from geograpy.locator import Locator
from geograpy.extraction import Extractor

# avoid tokeniser parrallelism
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def get_options():
    description = "Run sentiment analysis on twitter data."
    parser = argparse.ArgumentParser(description=description,
                                     prog='python __main__.py')

    IO = parser.add_argument_group('Input/options.out')
    IO.add_argument('--infile',
                    required=True,
                    help='Infile of tweets to process.')
    IO.add_argument('--outfile',
                    required=True,
                    help='Outfile prefix to save as .csv.')
    IO.add_argument('--debug',
                    action="store_true",
                    default=False,
                    help='Downsample to 100 tweets for debugging.')
    return parser.parse_args()

def map_location_analysis(row):
    user_location = row[1]
    followers = row[3]
    friends = row[4]
    favourites = row[5]
    verified = row[6]
    date_time = row[7]
    retweet = row[10]

    # get data/time
    date_time = datetime.strptime(date_time, '%d/%m/%Y %H:%M')

    # get location
    location = ("NA", "NA")
    if user_location != "" and user_location != None:
        location = get_location(user_location)
    return date_time, location, followers, friends, favourites, verified, retweet

def main():
    #options = get_options()

    # infile = options.infile
    # outfile = options.outfile
    # debug = options.debug

    infile = "../../data/vax_tweets.csv"
    outfile = "vax_tweets_parsed.csv"
    debug = True

    df = read_infile(infile)
    df_list = df.values.tolist()

    if debug:
        df_list = df_list[0:100]

    # generate lists to hold output
    info_list = []
    sentiment_list = []

    print("Running NLP analysis...")
    # generate model
    tokenizer, config, model = load_model()

    count = 0
    for row in df_list:
        # determine sentiment
        text = row[8]
        if isinstance(text, str):
            text = preprocess(text)
            sentiment_list.append(determine_sentiment(text, tokenizer, config, model))
        else:
            sentiment_list.append(["NA", 0])

        info_list.append(map_location_analysis(row))

        if count % 1000 == 0:
            print("At index: {}".format(count))

        count += 1

    print("Writing output...")
    with open(outfile + ".csv", "w") as o:
        o.write("Sentiment,Sentiment_score,Date_time,Location,Num_followers,Num_friends,Num_favourites,User_verified,Retweet\n")
        for i in range(len(sentiment_list)):
            top_sentiment, top_score = sentiment_list[i]

            date_time, location, followers, friends, favourites, verified, retweet = info_list[i]

            o.write("{},{},{},{},{},{},{},{},{}\n".format(top_sentiment, top_score, date_time, location[0] + ":" + location[1],
                                           int(followers), int(friends), int(favourites), verified, retweet))



if __name__ == "__main__":
    main()