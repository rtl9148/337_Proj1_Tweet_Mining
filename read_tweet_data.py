
import json

def read_tweet_text(file_name):
    with open(file_name,'r') as open_file:
        text_lines = [i['text'] for i in json.load(open_file)]
    return text_lines

if __name__ == '__main__':
    data_file = 'gg2013.json'
    text_lines = read_tweet_text(data_file) 
    for line_i in text_lines[:100]:
        print(line_i)

 