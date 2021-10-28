



import json

if __name__ == '__main__':
    
    data_year = '2013'
    
    data_file = 'gg{}.json'.format(data_year)
    with open(data_file,'r') as open_file:
        data_entry = json.load(open_file)
    data_time_text = [(i['timestamp_ms'],i['text']) for i in data_entry]
    data_time_text.sort()
    
    sorted_text = [i[1] for i in data_time_text]

