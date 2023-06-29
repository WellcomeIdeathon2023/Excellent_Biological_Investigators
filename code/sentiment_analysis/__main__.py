from parse_data import read_infile, get_location
from sentiment_analysis import *
from datetime import datetime
from multiprocessing import Pool
from functools import partial
from shared_memory import *
from tqdm import *

# avoid tokeniser parrallelism
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

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
    infile = "../../data/vax_tweets.csv"
    outfile = "vax_tweets_parsed.csv"

    threads = 4

    # generate model
    tokenizer, config, model = load_model()

    info_list = []

    sentiment_list = []

    df = read_infile(infile)
    df_list = df.values.tolist()

    df_list = df_list[0:100]

    print("Sentiment analysis...")
    count = 0
    for row in df_list:
        # determine sentiment
        text = row[8]
        text = preprocess(text)
        sentiment_list.append(determine_sentiment(text, tokenizer, config, model))
        if count % 1000 == 0:
            print("At index: {}".format(count))

        count += 1

    print("Geographic analysis...")
    with Pool(processes=threads) as pool:
        with tqdm(total=len(df_list)) as pbar:
            for tweet_tup in pool.map(map_location_analysis, df_list):
                info_list.append(tweet_tup)
                pbar.update()

    print("Writing output...")
    with open(outfile, "w") as o:
        o.write("Sentiment,Sentiment_score,Date_time,Location,Num_followers,Num_friends,Num_favourites,User_verified,Retweet\n")
        for i in range(len(sentiment_list)):
            top_sentiment, top_score = sentiment_list[i]
            date_time, location, followers, friends, favourites, verified, retweet = info_list[i]


            o.write("{},{},{},{},{},{},{},{},{}\n".format(top_sentiment, top_score, date_time, location[0] + ":" + location[1],
                                           int(followers), int(friends), int(favourites), verified, retweet))



if __name__ == "__main__":
    main()