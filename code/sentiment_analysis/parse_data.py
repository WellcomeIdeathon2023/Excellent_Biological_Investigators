import pandas as pd

def read_infile(infile):
    df = pd.read_csv(infile, delimiter=",", header=0)
    df['text'] = df['text'].replace('\n', ' ', regex=True)

    for index, row in df.iterrows():
        yield row