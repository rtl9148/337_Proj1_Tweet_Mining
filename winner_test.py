

import json, re
from data_counter import Item_Counter

winner_qoute_pattern = '\"((?:[A-Z]+[a-z]*[ ]?)+)\"'
winner_keyword_pattern = '(?:^|[\s@#:;\.,!])(WIN|WINS|WINNER|WINNING|win|wins|winner|winningWin|Wins|Winner|Winning|win|wins|winner|winning)(?![A-Za-z])'

def winner_extractor(entry_in):
    to_return = []
    if re.search(winner_keyword_pattern, entry_in):
        to_return = re.findall(winner_qoute_pattern, entry_in)
    return to_return

if __name__ == '__main__':
    
    data_year = '2015'
    entry_file = 'gg{}.json'.format(data_year)
    with open(entry_file,'r') as open_file:
        data_entry = json.load(open_file)
    text_lines = [i['text'] for i in data_entry]
    
    winner_count = Item_Counter()
    for ind_i, line_i in enumerate(text_lines):
        print(ind_i)
        winner_list = winner_extractor(line_i)
        for winner_i in winner_list:
            winner_count.count_item(winner_i.lower())
            
    output_file = '{}_testing_winner_count.txt'.format(data_year)
    with open(output_file, 'w', encoding='utf-8') as open_file:
        open_file.write('\n'.join([str(i[0])+' '+i[1] for i in winner_count.get_item_rank()]))
            