import json
import re
import os
import operator
#import spacy
#nlp = spacy.load('en_core_web_sm')
#from spacy import displacy
from collections import Counter
from textblob import TextBlob
import matplotlib.pyplot as plt

#Load tweets into a list
def make_tweet_list(file_name):
    with open(file_name,'r') as open_file:
        data_entries = json.load(open_file)
        data_lines = [i['text'] for i in data_entries]
    return data_lines

def read_tweet_time(file_name):
    with open(file_name,'r') as open_file:
        data_entry = json.load(open_file)
    data_time_text = [(i['timestamp_ms'],i['text']) for i in data_entry]
    data_time_text.sort()
    
    sorted_text = [i[1] for i in data_time_text]
    return data_time_text

def get_keyword_tweets(keyword, data_lines):
    keyword_tweets = []
    #filter tweets to include only host-related tweets
    for tweet in data_lines:
        if re.search(keyword, tweet[1].lower()):
            if "best" in keyword:
                keyword_tweets.append((tweet[0], tweet[1].replace("best","")))
            else:
                keyword_tweets.append(tweet)

    return keyword_tweets

def get_sentiment(tweets, category):
    #Find the sentiment
    polarities = []
    timestamps = []
    print(len(tweets))
    for tweet in tweets:
        blob = TextBlob(tweet[1])
        polarity = blob.sentiment.polarity
        avg_pol = (sum(polarities) + polarity) / (len(polarities) + 1)
        polarities.append(avg_pol)
        timestamps.append(tweet[0])

    average_pol = sum(polarities) / len(polarities)

    plt.plot(timestamps, polarities)
    print(type(timestamps[0]))
    plt.title("Average Sentiment Over Time for " + category)
    plt.xlabel("Time (ms)")
    plt.ylabel("Average Sentiment")
    plt.show()

    return average_pol


def get_sentiments_categories(tweets):
    #Get list of tweets for each category
    host_tweets = get_keyword_tweets("host", tweets)
    song_tweets = get_keyword_tweets("best original song - motion picture", tweets)
    animated_tweets = get_keyword_tweets("best animated feature film", tweets)
    cecil_tweets = get_keyword_tweets("cecil b. demille award", tweets)

    #Get the sentiment for each category
    host_sentiment = get_sentiment(host_tweets, "Host")
    song_sentiment = get_sentiment(song_tweets, "Best Original Song - Motion Picture")
    anim_sentiment = get_sentiment(animated_tweets, "Best Animated Feature Film")
    cecil_sentiment = get_sentiment(cecil_tweets, "Cecil B. Demille Award")

    #Print out sentiment in text
    print_sentiment(host_sentiment, "Host")
    print_sentiment(song_sentiment, "Best Original Song - Motion Picture")
    print_sentiment(anim_sentiment, "Best Animated Feature Film")
    print_sentiment(cecil_sentiment, "Cecil B. Demille Award")


def print_sentiment(sentiment, category):
    if sentiment >= .5:
        print("Sentiment for ", category, " is strongly positive (Polarity Score: ", sentiment)
    elif sentiment > 0 and sentiment < .5:
        print("Sentiment for ", category, " is weakly positive (Polarity Score: ", sentiment)
    elif sentiment == 0:
        print("Sentiment for ", category, " is neutral (Polarity Score: ", sentiment)
    elif sentiment < 0 and sentiment > -.5:
        print("Sentiment for ", category, " is weakly negative (Polarity Score: ", sentiment)
    elif sentiment <= -.5:
        print("Sentiment for ", category, " is strongly negative (Polarity Score: ", sentiment)




if __name__ == '__main__':
    data_file = 'gg2013.json'
    data_lines = read_tweet_time(data_file)

    get_sentiments_categories(data_lines)

    

    


