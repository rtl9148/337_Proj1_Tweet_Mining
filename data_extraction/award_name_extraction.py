
## This code defines a function that takes in Tweets data and extract potential award names.
## It uses the helper class Item_Counter from data_counter.py
## len_return is a default parameter that determines the number of strings returned.


import re
from data_counter import Item_Counter

award_keyword_pattern = '((?:BEST|Best|best)[\s\-]?(?:(?:[A-Z][a-z]*|[A-Z]+)[\s\-]?)*(?:[A-Z][a-z]*|[A-Z]+))'
stop_word_list = ['golden', 'globe','best']

def extract_award_name(text_lines, len_return = 22):
    
    all_award_word = Item_Counter()
    
    for line_i in text_lines:
        award_word_list = re.findall(award_keyword_pattern,line_i)
        for award_word_i in award_word_list:
            cut_words = []
            cur_ind = 1
            last_ind = 0
            while cur_ind < len(award_word_i):
                if award_word_i[cur_ind].isupper() and re.search('[a-z]',award_word_i[cur_ind-1]):
                    cut_words.append(award_word_i[last_ind:cur_ind])
                    last_ind = cur_ind
                cur_ind += 1
            if last_ind != cur_ind:
                cut_words.append(award_word_i[last_ind:])
            normalized_word = ' '.join(cut_words).lower()
            #normalized_word = re.sub(r'((?<=[a-z])[A-Z])', r' \1', award_word_i)
            all_award_word.count_item(normalized_word)
            
    
    all_award_pattern = [(award_rank_i[0],tuple(award_rank_i[1].split(' '))) for award_rank_i in all_award_word.get_item_rank()]
    all_word_count = Item_Counter()
    for cur_pattern_rank_i in all_award_pattern:
        for award_word_i in cur_pattern_rank_i[1]:
            if not award_word_i in stop_word_list:
                all_word_count.count_item(award_word_i, cur_pattern_rank_i[0])
    
    selection_criteria = len_return+5
    len_standard = 5
    reduced_each_turn = 1
    frequent_words = set([i[1] for i in all_word_count.get_item_rank()[:selection_criteria]])
    pattern_selector = []
    pattern_selected = {}
    for ind in range(len_return):
        cur_selector = []
        for cur_pattern_rank_i in all_award_pattern:
            if not cur_pattern_rank_i[1] in pattern_selected:
                cur_word_set = set(i for i in cur_pattern_rank_i[1])
                cur_pattern_score = len(cur_word_set.intersection(frequent_words))
                cur_selector.append((cur_pattern_score,cur_pattern_rank_i[1]))
        cur_selector.sort(reverse=True)
        top_pattern = cur_selector[0][1]
        pattern_selected[top_pattern] = True
        pattern_selector.append(' '.join(top_pattern))
        for award_word_i in list(set(top_pattern).intersection(frequent_words))[:reduced_each_turn]:
            frequent_words.remove(award_word_i)
    
    return pattern_selector
            
                    
        

