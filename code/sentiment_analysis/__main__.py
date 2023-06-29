from parse_data import read_infile, get_location
from sentiment_analysis import *
from datetime import datetime
from shared_memory import *
from tqdm import *
import argparse
import pandas as pd

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
    IO.add_argument('--sentiment',
                    default=None,
                    help='Infile pre-processed tweet sentiment.')
    IO.add_argument('--outfile',
                    required=True,
                    help='Outfile prefix to save as .csv.')
    IO.add_argument('--threads',
                    type=int,
                    default=1,
                    help='Number of threads. Default = 1.')
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
    options = get_options()

    infile = options.infile
    outfile = options.outfile
    threads = options.threads
    sentinent_file = options.sentiment
    debug = options.debug

    df = read_infile(infile)
    df_list = df.values.tolist()

    if debug:
        df_list = df_list[0:100]

    # generate lists to hold output
    info_list = []
    sentiment_list = []

    if sentinent_file == None:
        # generate model
        tokenizer, config, model = load_model()

        print("Sentiment analysis...")
        count = 0
        for row in df_list:
            # determine sentiment
            text = row[8]
            if isinstance(text, str):
                text = preprocess(text)
                sentiment_list.append(list(determine_sentiment(text, tokenizer, config, model)))
            else:
                sentiment_list.append(["NA", 0])
            if count % 1000 == 0:
                print("At index: {}".format(count))

            count += 1


        print("Writing sentiment output...")
        with open(outfile + "_sentiment.csv", "w") as o:
            o.write("Sentiment,Sentiment_score\n")
            for i in range(len(sentiment_list)):
                entry = sentiment_list[i]

                top_sentiment = entry[0]
                top_score = entry[1]

                o.write("{},{}\n".format(top_sentiment, top_score))
    else:
        sentiment_df = pd.read_csv(sentinent_file, delimiter=",", header=0)

        sentiment_list = sentiment_df.values.tolist()

    print("Geographic analysis...")
    with Pool(processes=threads) as pool:
        with tqdm(total=len(df_list)) as pbar:
            for tweet_tup in pool.map(map_location_analysis, df_list):
                info_list.append(tweet_tup)
                pbar.update()

    print("Writing whole output...")
    with open(outfile + ".csv", "w") as o:
        o.write("Sentiment,Sentiment_score,Date_time,Location,Num_followers,Num_friends,Num_favourites,User_verified,Retweet\n")
        for i in range(len(sentiment_list)):
            entry = sentiment_list[i]
            top_sentiment = entry[0]
            top_score = entry[1]

            date_time, location, followers, friends, favourites, verified, retweet = info_list[i]


            o.write("{},{},{},{},{},{},{},{},{}\n".format(top_sentiment, top_score, date_time, location[0] + ":" + location[1],
                                           int(followers), int(friends), int(favourites), verified, retweet))



if __name__ == "__main__":
    main()