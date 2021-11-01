'''Version 0.35'''

## The main program interacts with the autograder through this code
## *** To save computation, this code creates a json file for its dictionary of answer through create_answer() function and loads the file for all function calls
## *** Please run main() of gg_api.py to generate the answer file before calling its functions. The answer file path is defined by path_to_answer(), and load_answer() loads the answer file


OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

import os, json, time
from data_extraction import Category_Processing
from data_processing import Data_Processor
from award_name_extraction import extract_award_name



def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    answers_table = load_answer(year)
    hosts = answers_table['hosts']
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    data_proc = Data_Processor(year)
    awards = extract_award_name(data_proc.get_text_lines())
    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    answers_table = load_answer(year)
    nominees = {i: answers_table['award_data'][i]['nominees'] for i in answers_table['award_data']}
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    answers_table = load_answer(year)
    winners = {i: answers_table['award_data'][i]['winner'] for i in answers_table['award_data']}
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    answers_table = load_answer(year)
    presenters = {i: answers_table['award_data'][i]['presenters'] for i in answers_table['award_data']}
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    
    testing_years = ['2013','2015']
    for year_i in testing_years:
        create_answer(year_i)
    return


def create_answer(data_year, save_to_json=True):
    
    time_record = time.perf_counter()
    data_proc = Data_Processor(data_year)
    print('Data Loading Time: {}s'.format(time.perf_counter()-time_record))
    
    time_record = time.perf_counter()
    award_name_list = OFFICIAL_AWARDS_1315
    award_proc = Category_Processing(award_name_list)
    result_output = award_proc.make_extraction_answer(data_proc.get_imdb_name(), data_proc.get_imdb_title(), data_proc.get_text_lines())
    
    if save_to_json:
        with open(path_to_answer(data_year), 'w', encoding='utf-8') as open_file:
            json.dump(result_output,open_file)
        print('Data Processing Time: {}s'.format(time.perf_counter()-time_record))
    else:
        return result_output

def path_to_answer(data_year):    
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),data_year+'_award_extraction_answer.json')

def load_answer(data_year):
    with open(path_to_answer(data_year), 'r', encoding='utf-8') as open_file:
        answers_table = json.load(open_file)
    return answers_table


if __name__ == '__main__':
    main()
