import json
import re
import os
import operator
#import spacy
#nlp = spacy.load('en_core_web_sm')
#from spacy import displacy
from collections import Counter
from textblob import TextBlob

#Load tweets into a list
def make_tweet_list(file_name):
    with open(file_name,'r') as open_file:
        data_entries = json.load(open_file)
        data_lines = [i['text'] for i in data_entries]
    return data_lines

#timestamps 
#"timestamps_ms"

def get_keyword_tweets(keyword, data_lines):
    keyword_tweets = []
    #filter tweets to include only host-related tweets
    for tweet in data_lines:
        if re.search(keyword, tweet.lower()):
            keyword_tweets.append(tweet)

    #Remove word best from tweets
    if "best" in keyword:
        for i in range(len(keyword_tweets)):
            keyword_tweets[i] = keyword_tweets[i].replace("best", "")
    return keyword_tweets

def get_sentiment(tweets):
    #Find the sentiment
    polarities = []
    for tweet in tweets:
        blob = TextBlob(tweet)
        polarity = blob.sentiment.polarity
        polarities.append(polarity)
        #print("Tweet: ", tweet, ", ", "Polarity: ", polarity)
    
    average_pol = sum(polarities) / len(polarities)

    return average_pol


def get_sentiments_categories(tweets):
    #Get list of tweets for each category
    host_tweets = get_keyword_tweets("host", data_lines)
    song_tweets = get_keyword_tweets("best original song - motion picture", data_lines)
    animated_tweets = get_keyword_tweets("best animated feature film", data_lines)
    cecil_tweets = get_keyword_tweets("cecil b. demille award", data_lines)

    #Get the sentiment for each category
    host_sentiment = get_sentiment(host_tweets)
    song_sentiment = get_sentiment(song_tweets)
    anim_sentiment = get_sentiment(animated_tweets)
    cecil_sentiment = get_sentiment(cecil_tweets)

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
    data_lines = make_tweet_list(data_file)

    get_sentiments_categories(data_lines)

    

    


