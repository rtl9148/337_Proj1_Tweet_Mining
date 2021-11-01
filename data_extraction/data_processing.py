

## The code is not cleaned and properly commented due to the time limit.
## This code contains two classes Data_Processor that handles Tweets data and IMDB data and IMDB_Processor that handles IMDB data
## Data_Processor is initialized with the default parameter data_year. It loads and ready to send Tweets data when initiated and can get two types of IMDB data through IMDB_Processor.
## Data_Processor reads gg2013.json file in the same directory 
## IMDB_Processor reads and and saves files in /data directory. Pre processed json data from original IMDB data are available at /data directory, 
## but IMDB_Processor can always create such a reduced json data file through select_from_database method from IMDB's data (www.imdb.com/interfaces/)
## ***Files are checked when loaded for IMDB_Processor, so please make sure the pre-processed data for specific year are available at /data directory
## Examples are in __main__

import json, re, time, os, csv
import numpy as np
import spacy
from stanza.server import CoreNLPClient

from nltk.metrics import edit_distance

spacy_nlp = spacy.load("en_core_web_sm")


        

class Data_Processor():
    def __init__(self, data_year='2013'):
        self.data_entry = []
        self.text_lines = []
        self.text_users = []
        self.data_year = data_year
        
        self.imdb_proc = IMDB_Processor()
        self.imdb_proc.load_data(data_year)
        
        self.read_data_file(data_year)
        
    def read_data_file(self, data_year='2013'):
        entry_file = 'gg{}.json'.format(data_year)
        with open(entry_file,'r') as open_file:
            self.data_entry = json.load(open_file)
        self.text_lines = [i['text'] for i in self.data_entry]
        self.text_users = [str(i['user']['id']) for i in self.data_entry]
    
    def get_imdb_name(self):
        return self.imdb_proc.get_name_data(self.data_year)
    
    def get_imdb_title(self):
        return self.imdb_proc.get_title_data(self.data_year)
    
    def get_text_lines(self):
        return self.text_lines
    
    def get_answer_table(self):
        return self.data_answer
    

class IMDB_Processor():
    def __init__(self):
        self.file_dir = 'data'
        self.data_dir = 'data'
        self.name_file = 'name_data'
        self.title_file = 'title_data'
        self.rating_file = 'rating_data'
        self.principal_file = 'principal_data'
        
        self.data_name = {}
        self.data_title = []
        self.data_rating = []
        
    def select_from_database(self, data_year = '2013', rating_limit = 7.0, length_limit = 6):
        time_record = [time.perf_counter()]
        
        year_limit = int(data_year)        

        rating_table = {}
        votes_table = {}
        data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.file_dir, self.rating_file+'.tsv')
        with open(data_file, 'r', encoding='utf-8') as open_file:
            data_reader = csv.reader(open_file, delimiter="\t")
            next(data_reader, None)
            for entry_i in data_reader:
                rating_table[entry_i[0]] = float(entry_i[1])
                votes_table[entry_i[0]] = int(entry_i[2])
        
        time_record.append(time.perf_counter())
        selected_data = {}
        title_check_table = {}
        data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.file_dir, self.title_file+'.tsv')
        with open(data_file, 'r', encoding='utf-8') as open_file:
            data_reader = csv.reader(open_file, delimiter="\t")
            next(data_reader, None)
            for entry_i in data_reader:
                if entry_i[5].isdigit() and int(entry_i[5]) >= year_limit-1 and int(entry_i[5]) <= year_limit and entry_i[0] in rating_table and rating_table[entry_i[0]] >= rating_limit:
                    entry_key = entry_i[2]
                    entry_id = entry_i[0]
                    if entry_key in selected_data:
                        selected_data[entry_key].append({'id':entry_id, 'type': entry_i[1], 'genres': entry_i[8],})
                    else:
                        selected_data[entry_key] = [{'id':entry_id, 'type': entry_i[1], 'genres': entry_i[8],}]
                    title_check_table[entry_id] = entry_key
                        
        
        data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.data_dir, data_year+'_'+self.title_file+'.json')
        with open(data_file, 'w', encoding='utf-8') as open_file:
            json.dump(selected_data, open_file)
                
        
        time_record.append(time.perf_counter())
        person_title_table = {}
        data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.file_dir, self.principal_file+'.tsv')
        with open(data_file, 'r', encoding='utf-8') as open_file:
            data_reader = csv.reader(open_file, delimiter="\t")
            next(data_reader, None)
            for entry_i in data_reader:
                if entry_i[0] in title_check_table:
                    if entry_i[2] in person_title_table:
                        person_title_table[entry_i[2]].append((entry_i[0],entry_i[3]))
                    else:
                        person_title_table[entry_i[2]] = [(entry_i[0],entry_i[3])]
            
        selected_data = {}
        data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.file_dir, self.name_file+'.tsv')
        with open(data_file, 'r', encoding='utf-8') as open_file:
            data_reader = csv.reader(open_file, delimiter="\t")
            next(data_reader, None)
            for entry_i in data_reader:
                has_title = False
                title_rating = 0.
                title_name = set()
                title_prof = set()
                check_title = person_title_table[entry_i[0]] if entry_i[0] in person_title_table else []
                for title_link_i in check_title:
                    if title_link_i[0] in title_check_table:
                        has_title = True
                        title_rating = max(title_rating, rating_table[title_link_i[0]])
                        title_prof.add(title_link_i[1])
                        title_name.add(title_check_table[title_link_i[0]])
                entry_key = entry_i[1]
                if has_title and len(entry_key) >= length_limit and title_rating >= rating_limit and (not entry_i[3].isdigit() or int(entry_i[3]) >= 2010) :
                    if entry_key in selected_data:
                        selected_data[entry_key].append({'id':entry_i[0], 'prof': list(title_prof), 'title': list(title_name),})
                    else:
                        selected_data[entry_key] = [{'id':entry_i[0], 'prof': list(title_prof), 'title': list(title_name),}]
                        
        
        data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.data_dir, data_year+'_'+self.name_file+'.json')
        with open(data_file, 'w', encoding='utf-8') as open_file:
            json.dump(selected_data, open_file)
            
        time_record.append(time.perf_counter())
        print('IMDB Filtering Time: {}'.format(list(np.array(time_record[1:])-np.array(time_record[:-1]))))
        
    def get_name_data(self, data_year):
        self.load_data(data_year)
        return self.data_name
    
    def get_title_data(self, data_year):
        self.load_data(data_year)
        return self.data_title
        
    def load_data(self, data_year):
        
        time_record = time.perf_counter()
        
        data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.data_dir, data_year+'_'+self.name_file+'.json')
        with open(data_file, 'r', encoding='utf-8') as open_file:
            self.data_name = json.load(open_file)
        
        data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.data_dir, data_year+'_'+self.title_file+'.json')
        with open(data_file, 'r', encoding='utf-8') as open_file:
            self.data_title = json.load(open_file)
            
        #print('Daniel Day-Lewis' in self.data_name)
            
        print('IMDB Loading Time: {}'.format(time.perf_counter() - time_record))
        print('Loaded {} of name entries '.format(len(self.data_name)))
        print('Loaded {} of title entries '.format(len(self.data_title)))


if __name__ == '__main__':
    pass
    #data_year = '2013'
    
    #t_imdb = IMDB_Processor()
    #t_imdb.select_from_database(data_year=data_year)
    #t_imdb.load_data(data_year)

