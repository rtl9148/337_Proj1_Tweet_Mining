import json
import re
import os
import operator
#import spacy
#nlp = spacy.load('en_core_web_sm')
#from spacy import displacy
from collections import Counter
from textblob import TextBlob

#Clean tweets by removing tweets with the word 'presenter'
#B/C When getting hosts, sometimes presenters are returned.
def clean_tweets(data_lines):
    filtered_tweets = []
    for tweet in data_lines:
        #if "rt" not in tweet and "@" not in tweet and "http" not in tweet:
         #   filtered_tweets.append(tweet)
         if "presenter" not in tweet:
             filtered_tweets.append(tweet)
    #print('Number of Clean Tweets: ', len(filtered_tweets))
    return filtered_tweets

#Load tweets into a list
def make_tweet_list(file_name):
    with open(file_name,'r') as open_file:
        data_entries = json.load(open_file)
        data_lines = [i['text'] for i in data_entries]
    return data_lines

#Create dictionary with possible answers
def extract_info(data_lines):
    check_list = ['nominated']
    extract_line = '\"((?:[A-Z]+[a-z]*[ ]?)+)\"'
    #extract_line = "\w+\s\w+"
    count_table = {}
    for line_i in data_lines:
        is_valid = True
        for check_i in check_list:
            if not re.search(check_i, line_i.lower()):
                is_valid = False
        if is_valid:
            extract_keys = re.findall(extract_line,line_i)
            for key_i in extract_keys:
                key_normal = key_i.lower()
                if key_normal in count_table:
                    count_table[key_normal] += 1
                else:
                    count_table[key_normal] = 1
    return count_table


#Output the key with the most votes
def get_max_k (count_table):
    return max(count_table.items(), key=operator.itemgetter(1))[0]

def get_keyword_tweets(keyword, data_lines):
    host_tweets = []
    #filter tweets to include only host-related tweets
    for tweet in data_lines:
        if re.search(keyword, tweet.lower()):
            host_tweets.append(tweet)
    return host_tweets

def get_sentiment(tweets):
    #Find the sentiment
    polarities = []
    for tweet in tweets:
        blob = TextBlob(tweet)
        polarity = blob.sentiment.polarity
        polarities.append(polarity)
        print("Tweet: ", tweet, ", ", "Polarity: ", polarity)
    
    average_pol = sum(polarities) / len(polarities)

    return average_pol


def get_hosts(data_lines):
    host_tweets = []
    #filter tweets to include only host-related tweets
    for tweet in data_lines:
        if re.search('host', tweet.lower()):
            host_tweets.append(tweet)
    hosts = {}
    ent_list = []
    for tweet in host_tweets:
        ent_list = get_entities(tweet)
        str_list = str(ent_list)
        if str_list != '[]':
            if str_list in hosts:
                hosts[str_list] += 1
            else:
                hosts[str_list] = 1
    return hosts

def get_entities(tweet):
    doc = nlp(tweet)
    ent_list = []
    for entity in doc.ents:
        if entity.label_ == 'PERSON':
            if 'golden globe' not in entity.text.lower(): #golden globe is labeled as person
                ent_list.append(entity.text)
    #if ent_list:
    #    print(ent_list)
    return ent_list



if __name__ == '__main__':
    data_file = 'gg2013.json'
    data_lines = make_tweet_list(data_file)
    #filtered = clean_tweets(data_lines)
   # hosts = get_hosts(filtered)
    #print(hosts)
    #print('Host: ', get_max_k(hosts))
    host_tweets = get_keyword_tweets("host", data_lines)
    song_tweets = get_keyword_tweets("best original song - motion picture", data_lines)
    animated_tweets = get_keyword_tweets("best animated feature film", data_lines)
    cecil_tweets = get_keyword_tweets("cecil b. demille award", data_lines)
    #song_sentiment = get_sentiment(song_tweets)

    #print("Number of Tweets: ", len(host_tweets))
    #print("Best Original Song Sentiment: ", get_sentiment(song_tweets))
    print("Best animated feature film sentiment: ", get_sentiment(animated_tweets))
    #print("Cecil b Demille Sentiment: ", get_sentiment(cecil_tweets))

    

    


