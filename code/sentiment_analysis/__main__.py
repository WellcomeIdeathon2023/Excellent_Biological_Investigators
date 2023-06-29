from parse_data import read_infile
from sentiment_analysis import *

def main():
    infile = "../../data/vax_tweets.csv"
    outfile = "vax_tweets_parsed.csv"

    # generate model
    tokenizer, config, model = load_model()

    #sentiment_list = []

    #df = read_infile(infile)


    count = 0
    with open(outfile, "w") as o:
        o.write("Sentiment,Sentiment_score,Date_time,Location\n")
        for text, date_time, location in read_infile(infile):
            top_sentiment, top_score = determine_sentiment(text, tokenizer, config, model)

            o.write("{},{},{},{}\n".format(top_sentiment, top_score, date_time, location[0] + ", " + location[1]))

            #sentiment_list.append((top_sentiment, top_score, date_time, location))

            #if count % 100 == 0:
                #print("At index: {}".format(count))
            print(count)
            count += 1


        # o.write("Sentiment,Sentiment_score,Date_time,Location\n")
        # for entry in sentiment_list:
        #     top_sentiment, top_score, date_time, location = entry
        #     o.write("{},{},{},{}\n".format(top_sentiment, top_score, date_time, location))


if __name__ == "__main__":
    main()