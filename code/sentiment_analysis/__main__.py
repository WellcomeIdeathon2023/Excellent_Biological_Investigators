from parse_data import read_infile
from sentiment_analysis import *
from datetime import datetime

def main():
    infile = "../../data/vax_tweets.csv"
    # generate model
    tokenizer, config, model = load_model()


    for entry in read_infile(infile):
        # get sentiment
        text = entry['text']
        top_sentiment, top_score = determine_sentiment(text, tokenizer, config, model)

        #get date
        date_time_standard = datetime.strptime(entry['date'], '%d/%m/%Y %H:%M')

        # get location
        location = entry['user_location']

        test = 1


if __name__ == "__main__":
    main()