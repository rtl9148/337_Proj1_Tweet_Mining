


## The code is not cleaned and properly commented due to the time limit.
## This code contains Category_Processing() class, which is the main program for the information extraction process. 
## It uses Data_Processor() from data_processing.py that is responsible for loading the json data and the IMDB data. It also uses a helper class Item_Counter() from data_counter.py.
## This code uses SpaCy and nltk. nltk will require file downloading and updating through nltk.download('punkt') at line 25
## To generate the answer, Category_Processing requires and is initialized with a list of categories (award names)
## The method make_extraction_answer takes two types of IMDB data and the tweets data and return the answer dictionary in the proper format


import json, re, time, os
import numpy as np
from itertools import combinations

from data_processing import Data_Processor
from data_counter import Item_Counter

import spacy
from nltk.metrics import edit_distance
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import nltk

nltk.download('punkt')
spacy_nlp = spacy.load("en_core_web_sm")


## All hard coded words are here.
award_person_word_list = ['actor','actress','director','demille']
stop_word_list = ['goldenglobe', 'rt', 'best']
key_presenter_pattern = '(?:^|\s)(present|presented|presenting|presenter)(?:$|\s)'
key_host_pattern = '(?:^|\s)(host|hosted|hoster|hosting)(?:$|\s)'


class Category_Processing():
    def __init__(self, category_list):
        self.category_list = category_list
        self.spacy_token_list = [spacy_nlp(i) for i in self.category_list]
        
        self.special_word_pattern = '((?:(?:[A-Z][a-z]*|[A-Z]+)[\s\-]?)*(?:[A-Z][a-z]*|[A-Z]+))'
        self.lower_word_pattern = '((?:[a-z]+[\s\-]?)*[a-z]+)'
        
    def make_extraction_answer(self, imdb_name_data, imdb_title_data, text_lines):
        award_related_word, award_related_name, award_word_groups, award_words, category_connected_name, category_connected_title, award_host_name, award_presenter_name = self.search_related_word( imdb_name_data, imdb_title_data, text_lines)
        
        award_of_person = {}
        for award_i in self.category_list:
            award_of_person[award_i] = False
            for word_i in award_i.split(' '):
                if word_i in award_person_word_list:
                    award_of_person[award_i] = True
                    
        clean_output = {}
        presenter_rank_list = {}
        top_limit = 10
        for award_i, award_word_i, award_related_word_i, award_related_name_i, award_presenter_name_i in zip(self.category_list, award_words, award_related_word, award_related_name, award_presenter_name):
            related_word_rank = award_related_word_i.get_item_rank()
            related_name_rank = award_related_name_i.get_item_rank()
            #top_choice = []
            top_words = []
            for cur_rank in related_word_rank:
                is_valid = True
                for check_word in stop_word_list:
                    if re.search(check_word, cur_rank[1]):
                        is_valid = False
                        break
                if is_valid:
                    for check_word in award_word_i:
                        if re.search(check_word, cur_rank[1]):
                            is_valid = False
                            break
                if is_valid:
                    top_words.append(cur_rank[1])
# =============================================================================
#                     top_choice.append(cur_rank)
#                 if len(top_words) >= top_limit:
#                     break
# =============================================================================
            top_names = []
            for cur_rank in related_name_rank:
                is_valid = True
                for check_word in stop_word_list:
                    if re.search(check_word, cur_rank[1]):
                        is_valid = False
                        break
                if is_valid:
                    for check_word in award_word_i:
                        if re.search(check_word, cur_rank[1]):
                            is_valid = False
                            break
                if is_valid:
                    top_names.append(cur_rank[1])
                    #top_choice.append(cur_rank)
                if len(top_names) >= top_limit:
                    break
            #top_choice.sort(reverse=True)
            clean_output[award_i] = {'o':top_words,'p':top_names}
            #clean_output[award_i] = top_choice
            
            award_presenter_rank = award_presenter_name_i.get_item_rank()
            presenter_rank = []
            if award_of_person[award_i]:
                for rank_i in award_presenter_rank:
                    if rank_i[1] != clean_output[award_i]['p'][0]:
                        presenter_rank.append(rank_i[1])
                        
            else:
                for rank_i in award_presenter_rank:
                    presenter_rank.append(rank_i[1])
            presenter_rank_list[award_i] = presenter_rank
# =============================================================================
#         #print(clean_output)
#         print()
# =============================================================================
        answer_output = {}
        for award_i in clean_output:
            nominee_rank = []
            full_award_rank = []
            if award_of_person[award_i]:
                nominee_rank = [i[1] for i in category_connected_name[award_i].get_item_rank()]
                full_award_rank = clean_output[award_i]['p']
            else:
                nominee_rank = [i[1] for i in category_connected_title[award_i].get_item_rank()]
                full_award_rank = clean_output[award_i]['o']
            
            presenter_rank = presenter_rank_list[award_i]
            cur_ind = 0
            while len(nominee_rank) < 4 and cur_ind < len(full_award_rank):
                if not full_award_rank[cur_ind] in nominee_rank:
                    nominee_rank.append(full_award_rank[cur_ind])
                cur_ind += 1
            answer_output[award_i] = {'winner': clean_output[award_i]['p'][0] if clean_output[award_i]['p'] else '',
                                      'nominees': nominee_rank,
                                      'presenters': presenter_rank,} \
                if award_of_person[award_i] else \
                                     {'winner': clean_output[award_i]['o'][0]  if clean_output[award_i]['o'] else '',
                                      'nominees': nominee_rank,
                                      'presenters': presenter_rank,}
            
        result_output = {}
        result_output['award_data'] = answer_output     
        host_rank = []
        for rank_i in award_host_name.get_item_rank()[:4]:
            host_rank.append(rank_i[1])                      
        result_output['hosts'] = host_rank
        
        return result_output
            
# =============================================================================
#         output_dir = 'result'
#         output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),output_dir,data_year+'result.json')
#         with open(output_file, 'w', encoding='utf-8') as open_file:
#             json.dump(result_output,open_file)
# =============================================================================
        
        
    def search_related_word(self, imdb_name_data, imdb_title_data, text_lines):
        
        name_table = {i.lower(): [j['prof'] for j in imdb_name_data[i]] for i in imdb_name_data}
        title_table = {i.lower(): ' '.join([j['type'].replace(',',' ')+' '+j['genres'].replace(',',' ') for j in imdb_title_data[i]]) for i in imdb_title_data}
        
        word_groups, category_word_check_list, category_words = self.get_word_group()
        
        helper_word_group_list = []
        for cur_ind in range(len(word_groups)):
            helper_word_group_list.extend([[i[0], i[1], cur_ind, []] for i in word_groups[cur_ind]])
        
        category_word_check_table = self.build_word_group_table(helper_word_group_list, category_word_check_list)
        
        #debug
# =============================================================================
#         test_lines_1 = [[] for i in self.category_list]
#         test_lines_2 = [[] for i in self.category_list]
#         test_lines_3 = [[] for i in self.category_list]
#         test_lines_4 = [[] for i in self.category_list]
#         test_lines_5 = [[] for i in self.category_list]
#         test_lines_6 = []
#         test_lines_7 = []
#         test_lines_8 = [[] for i in self.category_list]
#         test_lines_9 = []
#         test_title_total = Item_Counter()
#         test_name_total = Item_Counter()
#         key_word_check_list_1 = [[data_proc.data_answer['award_data'][i]['winner']] for i in self.category_list]
#         key_word_check_list_2 = [data_proc.data_answer['award_data'][i]['nominees'] for i in self.category_list]
#         key_word_check_list_3 = [data_proc.data_answer['award_data'][i]['presenters'] for i in self.category_list]
#         key_word_check_list_4 = [host_list for i in self.category_list]
#         key_word_check_list_5 = [['hugh jackman', 'don cheadle'] for i in self.category_list]
#         
#         key_word_check_list_6 = ['\"((?:[A-Z]+[a-z]*[ ]?)+)\"']
#         test_quote_list = []
#         test_quote_count = [Item_Counter() for i in self.category_list]
# =============================================================================
        
        category_related_word = [Item_Counter() for i in word_groups]
        category_related_name = [Item_Counter() for i in word_groups]
        category_host_name = Item_Counter()
        category_presenter_name = [Item_Counter() for i in word_groups]
        category_found_word_table = {}
        category_title_count = [Item_Counter() for i in word_groups]
        category_name_count = [Item_Counter() for i in word_groups]
        cur_line_count = 0
        for line_i in text_lines:
            if cur_line_count%10000 == 0:
                print('{}/{}'.format(cur_line_count,len(text_lines)))
            cur_line_count += 1
            line_lower_i = line_i.lower()
            
            #debug
# =============================================================================
#             found_award = set()
#             top_award = set()
#             find_key_word_test = re.search(key_word_test_1, line_lower_i)
#             
#             #if find_key_word_test:
#             sentence_list = sent_tokenize(line_i)
#             #for sentence_i in sentence_list:
#             #    sentence_lower_i = sentence_i.lower()
# =============================================================================
            
            special_words_lower = [i.lower() for i in self.find_all_special_word(line_i)]
            title_list_lower = []
            name_list_lower = []
            for special_i in special_words_lower:
                if special_i in name_table:
                    name_list_lower.append(special_i)
                    
                    #debug
                    #test_name_total.count_item(special_i)
                    
                if special_i in title_table:
                    title_list_lower.append(special_i)
                    
                    #debug
                    #test_title_total.count_item(special_i)
            
            presenter_flag = re.search(key_presenter_pattern, line_lower_i)
            host_flag = re.search(key_host_pattern, line_lower_i)
            
            if host_flag:
                for word_lower_i in name_list_lower:
                    category_host_name.count_item(word_lower_i)
            
            #older version
# =============================================================================
#             special_words_lower = [ ]
#             for word_i in self.find_all_special_word(line_i):
#                 word_lower_i = word_i.lower()
#                 if word_lower_i in name_table or word_lower_i in title_table:
#                     special_words_lower.append(word_lower_i)
# =============================================================================
            
            for word_i in category_word_check_list:
                category_found_word_table[word_i] = True if re.search(word_i.replace('.','\.'), line_lower_i) else False
            found_category = self.check_word_group_table([], category_word_check_list, category_word_check_table, category_found_word_table)
            found_rank = found_category.get_item_rank()
            if found_rank:
                top_count = found_rank[0][0]
                cur_ind = 0
                while cur_ind < len(found_rank) and found_rank[cur_ind][0] == top_count:
                    
                    #debug
                    #top_award.add(found_rank[cur_ind][1])
                    
                    category_related_word_i = category_related_word[found_rank[cur_ind][1]]
                    category_related_name_i = category_related_name[found_rank[cur_ind][1]]
                    category_presenter_name_i = category_presenter_name[found_rank[cur_ind][1]]
                    
                    for word_lower_i in name_list_lower:
                        category_related_name_i.count_item(word_lower_i)
                    for word_lower_i in title_list_lower:
                        category_related_word_i.count_item(word_lower_i)
                        
                    if presenter_flag:
                        for word_lower_i in name_list_lower:
                            category_presenter_name_i.count_item(word_lower_i)
                        
                    connected_lower_limit = 2
                    if len(title_list_lower) >= connected_lower_limit:
                        for word_lower_i in title_list_lower:
                            category_title_count[found_rank[cur_ind][1]].count_item(word_lower_i)
                    if len(name_list_lower) >= connected_lower_limit:
                        for word_lower_i in name_list_lower:
                            category_name_count[found_rank[cur_ind][1]].count_item(word_lower_i)
                            
                    cur_ind += 1
                            
                            
                    # older version
# =============================================================================
#                     for ner_i in ner_list_i:
#                         if ner_i['label'] == 'PERSON':
#                             name_word_i = self.find_lower_word(ner_i['text'].lower())
#                             if name_word_i:
#                                 category_related_name_i.count_item(name_word_i)
#                             if name_word_i in special_words_lower:
#                                 special_words_lower.remove(name_word_i)
#                     for special_i in special_words_lower:
#                         category_related_word_i.count_item(special_i)
# =============================================================================

                #debug
# =============================================================================
#                 found_award.update([i for i in found_rank])
#                     
#             
#             #debug
#             if found_award:
#                 found_award_str = ' '.join([data_proc.data_answer['award_data'][self.category_list[found_i[1]]]['winner']+':'+str(found_i[0]) for found_i in found_award])
#                 for award_ind in range(len(self.category_list)):
#                     if award_ind in top_award:
#                         line_key_words = set()
#                         for key_word_i in key_word_check_list_1[award_ind]:
#                             if re.search(key_word_i, line_i.lower()):
#                                 line_key_words.add(key_word_i)
#                         line_key_words = list(line_key_words)
#                         if line_key_words:
#                             award_str_i = data_proc.data_answer['award_data'][self.category_list[award_ind]]['winner']
#                             test_lines_1[award_ind].append(found_award_str+' ('+str(len(line_key_words))+')['+', '.join(line_key_words)+']:\n'+line_i)
#                         
#                         line_key_words = set()
#                         for key_word_i in key_word_check_list_2[award_ind]:
#                             if re.search(key_word_i, line_i.lower()):
#                                 line_key_words.add(key_word_i)
#                         line_key_words = list(line_key_words)
#                         if line_key_words:
#                             award_str_i = data_proc.data_answer['award_data'][self.category_list[award_ind]]['winner']
#                             test_lines_2[award_ind].append(found_award_str+' ('+str(len(line_key_words))+')['+', '.join(line_key_words)+']:\n'+line_i)
#                             
#                         line_key_words = set()
#                         for key_word_i in key_word_check_list_3[award_ind]:
#                             if re.search(key_word_i, line_i.lower()):
#                                 line_key_words.add(key_word_i)
#                         line_key_words = list(line_key_words)
#                         if line_key_words:
#                             award_str_i = data_proc.data_answer['award_data'][self.category_list[award_ind]]['winner']
#                             test_lines_3[award_ind].append(found_award_str+' ('+str(len(line_key_words))+')['+', '.join(line_key_words)+']:\n'+line_i)
#                             
#                         line_key_words = set()
#                         for key_word_i in key_word_check_list_4[award_ind]:
#                             if re.search(key_word_i, line_i.lower()):
#                                 line_key_words.add(key_word_i)
#                         line_key_words = list(line_key_words)
#                         if line_key_words:
#                             award_str_i = data_proc.data_answer['award_data'][self.category_list[award_ind]]['winner']
#                             test_lines_4[award_ind].append(found_award_str+' ('+str(len(line_key_words))+')['+', '.join(line_key_words)+']:\n'+line_i)
#                             
#                         line_key_words = set()
#                         for key_word_i in key_word_check_list_5[award_ind]:
#                             if re.search(key_word_i, line_i.lower()):
#                                 line_key_words.add(key_word_i)
#                         line_key_words = list(line_key_words)
#                         if line_key_words:
#                             award_str_i = data_proc.data_answer['award_data'][self.category_list[award_ind]]['winner']
#                             test_lines_5[award_ind].append(found_award_str+' ('+str(len(line_key_words))+')['+', '.join(line_key_words)+']:\n'+line_i)
#                         
#                 line_key_words = set()
#                 for key_word_i in key_word_check_list_6:
#                     search_key_word = re.findall(key_word_i, line_i)
#                     if search_key_word:
#                         line_key_words.update([i.lower() for i in search_key_word])
#                 line_key_words = list(line_key_words)
#                 if line_key_words:
#                     test_quote_list.append([[self.category_list[i[1]] for i in found_award],line_key_words])
#                     for line_key_word_i in line_key_words:
#                         for found_i in found_award:
#                             test_quote_count[found_i[1]].count_item(line_key_word_i)
#                     test_lines_6.append(found_award_str+'\n('+str(len(line_key_words))+')['+', '.join(line_key_words)+']:\n'+line_i)
#                     
# # =============================================================================
# #                 line_key_words = set()
# #                 for ner_i in ner_list_i:
# #                     if ner_i['label'] == 'PERSON':
# #                         line_key_words.add(self.find_lower_word(ner_i['text'].lower()))
# # =============================================================================
#                 line_key_words = list(line_key_words)
#                 if len(line_key_words) >= 3 and all(line_key_words):
#                     test_lines_7.append(found_award_str+'\n('+str(len(line_key_words))+')['+', '.join(line_key_words)+']:\n'+line_i)
#             
#         #debug
#         output_dir = 'test_related_word'
#         for award_ind in range(len(self.category_list)):
#             output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),output_dir,'03_testing_view_award_{}_related_line_1.txt'.format(award_ind))
#             with open(output_file, 'w', encoding='utf-8') as open_file:
#                 open_file.write(self.category_list[award_ind]+'\n\n'+'\n'.join(test_lines_1[award_ind]))
#             output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),output_dir,'03_testing_view_award_{}_related_line_2.txt'.format(award_ind))
#             with open(output_file, 'w', encoding='utf-8') as open_file:
#                 open_file.write(self.category_list[award_ind]+'\n\n'+'\n'.join(test_lines_2[award_ind]))
#             output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),output_dir,'03_testing_view_award_{}_related_line_3.txt'.format(award_ind))
#             with open(output_file, 'w', encoding='utf-8') as open_file:
#                 open_file.write(self.category_list[award_ind]+'\n\n'+'\n'.join(test_lines_3[award_ind]))
#             output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),output_dir,'03_testing_view_award_{}_related_line_4.txt'.format(award_ind))
#             with open(output_file, 'w', encoding='utf-8') as open_file:
#                 open_file.write(self.category_list[award_ind]+'\n\n'+'\n'.join(test_lines_4[award_ind]))
#             output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),output_dir,'03_testing_view_award_{}_related_line_5.txt'.format(award_ind))
#             with open(output_file, 'w', encoding='utf-8') as open_file:
#                 open_file.write(self.category_list[award_ind]+'\n\n'+'\n'.join(test_lines_5[award_ind]))
#         output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),output_dir,'03_testing_view_award_related_line_6.txt')
#         with open(output_file, 'w', encoding='utf-8') as open_file:
#             open_file.write('\n'.join(test_lines_6))
#         output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),output_dir,'03_testing_view_award_related_line_7.txt')
#         with open(output_file, 'w', encoding='utf-8') as open_file:
#             open_file.write('\n'.join(test_lines_7))
# =============================================================================
        
        category_connected_name = {self.category_list[i]: category_name_count[i] for i in range(len(self.category_list))}
        category_connected_title = {self.category_list[i]: category_title_count[i] for i in range(len(self.category_list))}
        
# =============================================================================
#         output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),output_dir,'03_testing_view_name_count.txt')
#         with open(output_file, 'w', encoding='utf-8') as open_file:
#             open_file.write('\n'.join([self.category_list[i]+':\n'+str(category_name_count[i].get_item_rank())+'\n\n' for i in range(len(self.category_list))]))
#         output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),output_dir,'03_testing_view_title_count.txt')
#         with open(output_file, 'w', encoding='utf-8') as open_file:
#             open_file.write('\n'.join([self.category_list[i]+':\n'+str(category_title_count[i].get_item_rank())+'\n\n' for i in range(len(self.category_list))]))
#         output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),output_dir,'03_testing_view_name_total.txt')
#         with open(output_file, 'w', encoding='utf-8') as open_file:
#             open_file.write('\n'.join([str(i) for i in test_name_total.get_item_rank()]))
#         output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),output_dir,'03_testing_view_title_total.txt')
#         with open(output_file, 'w', encoding='utf-8') as open_file:
#             open_file.write('\n'.join([str(i) for i in test_title_total.get_item_rank()]))
#                     
#         
#         
#         #debug
#         output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),output_dir,'03_testing_view_test_quote_list.txt')
#         with open(output_file, 'w', encoding='utf-8') as open_file:
#             open_file.write('\n'.join(['\n'.join([str(j) for j in i]) for i in test_quote_list]))
#         output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),output_dir,'03_testing_view_test_quote_count.txt')
#         with open(output_file, 'w', encoding='utf-8') as open_file:
#             open_file.write('\n'.join([i+'\n'+str(j.get_item_rank())+'\n' for i,j in zip(self.category_list, test_quote_count)]))
# =============================================================================
                    
        
        return category_related_word, category_related_name, word_groups, category_words, category_connected_name, category_connected_title, category_host_name, category_presenter_name
        
                
    def find_lower_word(self, str_in):
        search_result = re.search(self.lower_word_pattern,str_in)
        return search_result[1] if search_result else search_result
    
    def find_all_special_word(self, str_in):
        return re.findall(self.special_word_pattern,str_in)
        
    def get_word_group(self):
        # TO DO: lower case
        word_count = Item_Counter()
        category_words = []
        word_categorys = {}
        cur_ind = 0
        for category_token_i, category_i in zip(self.spacy_token_list, self.category_list):
            word_group = set()
            for token_i in category_token_i:
                if not token_i.is_stop and re.search('[a-z]', token_i.text):
                    cur_word = token_i.text
                    word_count.count_item(cur_word)
                    word_group.add(cur_word)
                    if cur_word in word_categorys:
                        word_categorys[cur_word].add(cur_ind)
                    else:
                        word_categorys[cur_word] = {cur_ind}
            category_words.append(word_group)
            cur_ind += 1
        #word_rank = word_count.get_item_rank(reverse_order=False)
        
        all_category_words_set = set()
        for category_words_i in category_words:
            all_category_words_set.update(category_words_i)
        
        word_group_limit = 4
        word_groups = []
        word_choice_hit_count = Item_Counter()
        for cur_ind in range(len(category_words)):
            pos_word_choice = category_words[cur_ind].copy()
            neg_word_choice = all_category_words_set.difference(pos_word_choice)
            word_num = 1
            cur_unique_word = []
            while len(pos_word_choice) > 0 and word_num <= min(len(pos_word_choice),word_group_limit):
                for neg_word_num_limit in range(min(len(neg_word_choice)+1, word_group_limit - word_num + 1, word_num)):
                    pos_choice_list = [i for i in combinations(pos_word_choice, word_num)]
                    neg_choice_list = []
                    for neg_word_num_i in range(neg_word_num_limit+1):
                        if neg_word_num_i <= len(neg_word_choice):
                            neg_choice_list.extend([i for i in combinations(neg_word_choice, neg_word_num_i)])
                    pos_selected_word = {}
                    neg_selected_word = {}
                    for pos_choice_i in pos_choice_list:
                        for neg_choice_i in neg_choice_list:
                            choice_category = set([i for i in range(len(category_words))])
                            for word_i in pos_choice_i:
                                choice_category = choice_category.intersection(word_categorys[word_i])
                            for word_i in neg_choice_i:
                                choice_category = choice_category.difference(word_categorys[word_i])
                            if len(choice_category) == 1:
                                cur_unique_word.append((pos_choice_i, neg_choice_i))
                                for word_i in pos_choice_i:
                                    pos_selected_word[word_i] = True
                                for word_i in neg_choice_i:
                                    neg_selected_word[word_i] = True
                    for word_i in pos_selected_word:
                        pos_word_choice.remove(word_i)
                        word_choice_hit_count.count_item(word_i)
                    for word_i in neg_selected_word:
                        neg_word_choice.remove(word_i)
                        word_choice_hit_count.count_item(word_i)
                word_num += 1
            word_groups.append(cur_unique_word)
        category_word_check_list = [i[1] for i in word_choice_hit_count.get_item_rank()]
        
        return word_groups, category_word_check_list, category_words
                            
    #TO DO check lower case
    def build_word_group_table(self, word_group_list, word_check_list):
        word_check_table = {}
        cur_word_group_list = word_group_list
        for word_ind in range(len(word_check_list)):
            cur_word = word_check_list[word_ind]
            #debug
# =============================================================================
#             to_print = str(cur_word) +str( len(word_check_list))+str( word_check_list)+'\n'+'\n'.join([str(i) for i in cur_word_group_list])+'\n'
#             for test_ind in range(len(cur_word_group_list)):
#                 for test_ind_2 in range(test_ind+1, len(cur_word_group_list)):
#                     assert cur_word_group_list[test_ind] != cur_word_group_list[test_ind_2], to_print+str(cur_word_group_list[test_ind])+' '+str(cur_word_group_list[test_ind_2])
# =============================================================================
                    
            next_word_group_list = []
            check_word_group_list = []
            complete_word_group_list = []
            for word_group_i in cur_word_group_list:
                if cur_word in word_group_i[0] or cur_word in word_group_i[1]:
                    if cur_word in word_group_i[0]:
                        word_group_i[3].append(True)
                    else:
                        word_group_i[3].append(False)
                    if len(word_group_i[0]) + len(word_group_i[1]) <= len(word_group_i[3]):
                        complete_word_group_list.append(word_group_i)
                    else:
                        check_word_group_list.append(word_group_i)
                else:
                    next_word_group_list.append(word_group_i)
            #debug
            #print(next_word_group_list)
            #print()
            #print(check_word_group_list)
            #print()
            #print(complete_word_group_list)
            #print()
            if check_word_group_list:
                cur_check_table = self.build_word_group_table(check_word_group_list, word_check_list[word_ind+1:])
            else:
                cur_check_table = {}
            if complete_word_group_list:
                for unique_group in complete_word_group_list:
                    assert (not tuple(unique_group[3]) in cur_check_table), '{}\n\n{}\n\n{}'.format(next_word_group_list,check_word_group_list,complete_word_group_list)
                    cur_check_table[tuple(unique_group[3])] = unique_group[2]
                #debug
                #print(cur_check_table)
            if cur_check_table:
                word_check_table[cur_word] = cur_check_table
            cur_word_group_list = next_word_group_list
        return word_check_table
    
    #TO DO check lower case
    def check_word_group_table(self, found_word_list, word_check_list, check_table, found_word_table):
        found_category = Item_Counter()
        for cur_ind in range(len(word_check_list)):
            cur_word = word_check_list[cur_ind]
            if cur_word in check_table:
                found_category.merge_counter(self.check_word_group_table(found_word_list+[found_word_table[cur_word]], word_check_list[cur_ind+1:], check_table[cur_word], found_word_table))
            found_word_key = tuple(found_word_list)
            if found_word_key in check_table:
                found_category.count_item(check_table[found_word_key])
        return found_category




# =============================================================================
# if __name__ == '__main__':
#     
#     data_year = '2013'
#     time_record = time.perf_counter()
#     data_proc = Data_Processor(data_year)
#     _, _, _, _, _, award_name_list = data_proc.answer_components()
#     print('Data Loading Time: {}'.format(time.perf_counter()-time_record))
#     
#     #print('{\'hosts\': '+str(data_proc.data_answer['hosts'])+',\n\'award_data\': {\n'+'\n'.join(['\'{}\': {},'.format(i,data_proc.data_answer['award_data'][i]) for i in data_proc.data_answer['award_data']])+'\n}}')
#     
#     time_record = time.perf_counter()
#     award_proc = Category_Processing(award_name_list)
#     result_output = award_proc.make_extraction_answer(data_proc.get_imdb_name(), data_proc.get_imdb_title(), data_proc.get_text_lines())
#     
#     output_dir = 'result'
#     output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),output_dir,data_year+'result_2_4.json')
#     with open(output_file, 'w', encoding='utf-8') as open_file:
#         json.dump(result_output,open_file)
#     
# =============================================================================
    
    #debug
# =============================================================================
#     award_related_word, award_related_name, award_word_groups, award_words, category_connected_name, category_connected_title, award_host_name, award_presenter_name = award_proc.search_related_word(data_proc.get_text_lines(), data_proc.get_spacy_ner(data_year))
#     print('Data Processing Time: {}'.format(time.perf_counter()-time_record))
#     
#     output_file = '{}_testing_award_related_word.txt'.format(data_year)
#     with open(output_file, 'w', encoding='utf-8') as open_file:
#         open_file.write('\n'.join([str(i)+'\n'+str(j)+'\n'+str(k)+'\n'+str(l.get_item_rank())+'\n' for i,j,k,l in zip(self.category_list, award_words, award_word_groups, award_related_word)]))
#         
#     output_file = '{}_testing_award_related_name.txt'.format(data_year)
#     with open(output_file, 'w', encoding='utf-8') as open_file:
#         open_file.write('\n'.join([str(i)+'\n'+str(j)+'\n'+str(k)+'\n'+str(l.get_item_rank())+'\n' for i,j,k,l in zip(self.category_list, award_words, award_word_groups, award_related_name)]))
#         
#     output_file = '{}_testing_award_host_name.txt'.format(data_year)
#     with open(output_file, 'w', encoding='utf-8') as open_file:
#         open_file.write('\n'.join([str(i) for i in award_host_name.get_item_rank()]))
#         
#     output_file = '{}_testing_award_presenter_name.txt'.format(data_year)
#     with open(output_file, 'w', encoding='utf-8') as open_file:
#         open_file.write('\n'.join([str(i)+'\n'+str(j)+'\n'+str(k)+'\n'+str(l.get_item_rank())+'\n' for i,j,k,l in zip(self.category_list, award_words, award_word_groups, award_presenter_name)]))
# # =============================================================================
# #     for award_ind in range(len(self.category_list)):
# #         output_file = '{}_testing_award_{}_related_word.txt'.format(data_year,award_ind)
# #         with open(output_file, 'w', encoding='utf-8') as open_file:
# #             open_file.write(str(self.category_list[award_ind])+'\n'+str(award_words[award_ind])+'\n'+str(award_word_groups[award_ind])+'\n'+str(award_related_word[award_ind].get_item_rank()))
# #             
# #         output_file = '{}_testing_award_{}_related_name.txt'.format(data_year,award_ind)
# #         with open(output_file, 'w', encoding='utf-8') as open_file:
# #             open_file.write(str(self.category_list[award_ind])+'\n'+str(award_words[award_ind])+'\n'+str(award_word_groups[award_ind])+'\n'+str(award_related_name[award_ind].get_item_rank()))
# # =============================================================================
#         
#     award_of_person = {}
#     award_person_word_list = ['actor','actress','director','demille']
#     for award_i in self.category_list:
#         award_of_person[award_i] = False
#         for word_i in award_i.split(' '):
#             if word_i in award_person_word_list:
#                 award_of_person[award_i] = True
#                 
#     clean_output = {}
#     presenter_rank_list = {}
#     stop_word_list = ['goldenglobe', 'rt', 'best']
#     top_limit = 10
#     for award_i, award_word_i, award_related_word_i, award_related_name_i, award_presenter_name_i in zip(self.category_list, award_words, award_related_word, award_related_name, award_presenter_name):
#         related_word_rank = award_related_word_i.get_item_rank()
#         related_name_rank = award_related_name_i.get_item_rank()
#         top_choice = []
#         top_words = []
#         for cur_rank in related_word_rank:
#             is_valid = True
#             for check_word in stop_word_list:
#                 if re.search(check_word, cur_rank[1]):
#                     is_valid = False
#                     break
#             if is_valid:
#                 for check_word in award_word_i:
#                     if re.search(check_word, cur_rank[1]):
#                         is_valid = False
#                         break
#             if is_valid:
#                 top_words.append(cur_rank[1])
#                 top_choice.append(cur_rank)
#             if len(top_words) >= top_limit:
#                 break
#         top_names = []
#         for cur_rank in related_name_rank:
#             is_valid = True
#             for check_word in stop_word_list:
#                 if re.search(check_word, cur_rank[1]):
#                     is_valid = False
#                     break
#             if is_valid:
#                 for check_word in award_word_i:
#                     if re.search(check_word, cur_rank[1]):
#                         is_valid = False
#                         break
#             if is_valid:
#                 top_names.append(cur_rank[1])
#                 top_choice.append(cur_rank)
#             if len(top_names) >= top_limit:
#                 break
#         top_choice.sort(reverse=True)
#         clean_output[award_i] = {'o':top_words,'p':top_names}
#         #clean_output[award_i] = top_choice
#         
#         award_presenter_rank = award_presenter_name_i.get_item_rank()
#         presenter_rank = []
#         if award_of_person[award_i]:
#             for rank_i in award_presenter_rank:
#                 if rank_i[1] != clean_output[award_i]['p'][0]:
#                     presenter_rank.append(rank_i[1])
#                     
#         else:
#             for rank_i in award_presenter_rank:
#                 presenter_rank.append(rank_i[1])
#         presenter_rank_list[award_i] = presenter_rank
#     #print(clean_output)
#     print()
#     answer_output = {}
#     award_person_word_list = ['actor','actress','director','demille']
#     for award_i in clean_output:
#         #answer_output[award_i] = {'winner': clean_output[award_i][0][0]+' '+clean_output[award_i][1][0]}
#         award_of_person = False
#         for word_i in award_i.split(' '):
#             if word_i in award_person_word_list:
#                 award_of_person = True
#         nominee_rank = []
#         full_award_rank = []
#         print(category_connected_name)
#         print(category_connected_title)
#         if award_of_person:
#             nominee_rank = [i[1] for i in category_connected_name[award_i].get_item_rank()]
#             full_award_rank = clean_output[award_i]['p']
#         else:
#             nominee_rank = [i[1] for i in category_connected_title[award_i].get_item_rank()]
#             full_award_rank = clean_output[award_i]['o']
#         
#         presenter_rank = presenter_rank_list[award_i]
#         cur_ind = 0
# # =============================================================================
# #         while len(nominee_rank) < 6 and cur_ind < len(full_award_rank):
# #             if not full_award_rank[cur_ind] in nominee_rank:
# #                 nominee_rank.append(full_award_rank[cur_ind])
# #             cur_ind += 1
# # =============================================================================
#         print(nominee_rank)
#         answer_output[award_i] = {'winner': clean_output[award_i]['p'][0] if clean_output[award_i]['p'] else '',
#                                   'nominees': nominee_rank,
#                                   'presenters': presenter_rank,} \
#             if award_of_person else \
#                                  {'winner': clean_output[award_i]['o'][0]  if clean_output[award_i]['o'] else '',
#                                   'nominees': nominee_rank,
#                                   'presenters': presenter_rank,}
#         
#     result_output = {}
#     result_output['award_data'] = answer_output     
#     host_rank = []
#     for rank_i in award_host_name.get_item_rank()[:4]:
#         host_rank.append(rank_i[1])                      
#     result_output['hosts'] = host_rank
#         
#     output_dir = 'result'
#     output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),output_dir,data_year+'result.json')
#     with open(output_file, 'w', encoding='utf-8') as open_file:
#         json.dump(result_output,open_file)
# =============================================================================
        
                    
    
    
    
# =============================================================================
#     word_count = Item_Counter()
#     award_words = []
#     word_awards = {}
#     cur_ind = 0
#     for award_token_i, award_i in zip(award_spacy_token_list, self.category_list):
#         word_groups = []
#         word_group = []
#         for token_i in award_token_i:
#             if not token_i.is_stop and re.search('[a-z]', token_i.text):
#                 cur_word = token_i.text
#                 word_count.count_item(cur_word)
#                 word_group.append(cur_word)
#                 if cur_word in word_awards:
#                     word_awards[cur_word].append(cur_ind)
#                 else:
#                     word_awards[cur_word] = [cur_ind]
#         award_words.append(word_group)
#         cur_ind += 1
#     word_rank = word_count.get_item_rank(reverse_order=False)
#     
#     unique_words = []
#     for cur_ind in range(len(award_words)):
#         word_choice = award_words[cur_ind].copy()
#         word_num = 1
#         cur_unique_word = []
#         found_word = False
#         while not found_word and len(word_choice) > 0 and word_num <= len(word_choice):
#             choice_list = combinations(word_choice, word_num)
#             selected_word = {}
#             for choice_i in choice_list:
#                 #print(choice_i)
#                 choice_award = set([i for i in range(len(award_words))])
#                 #print(choice_award)
#                 for word_i in choice_i:
#                     choice_award = choice_award.intersection(set(word_awards[word_i]))
#                     #print(choice_award)
#                 if len(choice_award) == 1:
#                     cur_unique_word.append(choice_i)
#                     for word_i in choice_i:
#                         selected_word[word_i] = True
#                     # testing
#                     #found_word = True
#                     #break
#             for word_i in selected_word:
#                 word_choice.remove(word_i)
#             word_num += 1
#         unique_words.append(cur_unique_word)
#     
#     
#     output_file = '{}_testing_award_split.txt'.format(data_year)
#     with open(output_file, 'w', encoding='utf-8') as open_file:
#         open_file.write('\n'.join([str(i)+'\n'+str(j)+'\n'+str(k)+'\n' for i,j,k in zip(self.category_list, award_words,unique_words)]))
#         
#     award_related_word = [Item_Counter() for i in unique_words]
#     award_related_name = [Item_Counter() for i in unique_words]
#     cur_line_count = 0
#     for line_i, ner_list_i in zip(data_proc.get_text_lines(), data_proc.get_spacy_ner(data_year)):
#         if cur_line_count%1000 == 0:
#             print(cur_line_count)
#             to_print = False
#         else:
#             to_print = False
#         cur_line_count += 1
#         capital_words_lower = [i.lower() for i in re.findall(capital_word_pattern,line_i)]
#         line_lower_i = line_i.lower()
#         found_award = 0
#         
#         for award_ind in range(len(unique_words)):
#             cur_check =  unique_words[award_ind] and any([all([re.search(word_i.replace('.','\.'),line_lower_i) for word_i in word_group_i]) for word_group_i in unique_words[award_ind]])
#             if cur_check:
#                 found_award += 1
#                 award_related_word_i = award_related_word[award_ind]
#                 award_related_name_i = award_related_name[award_ind]
#         if found_award == 1:
#             for ner_i in ner_list_i:
#                 if ner_i['label'] == 'PERSON':
#                     award_related_name_i.count_item(ner_i['text'])
#                     name_word_i = ner_i['text'].lower()
#                     if name_word_i in capital_words_lower:
#                         capital_words_lower.remove(name_word_i)
#             for word_i in capital_words_lower:
#                 award_related_word_i.count_item(word_i)
#                     
#         
#         
#     
#     output_file = '{}_testing_award_related_word.txt'.format(data_year)
#     with open(output_file, 'w', encoding='utf-8') as open_file:
#         open_file.write('\n'.join([str(i)+'\n'+str(j)+'\n'+str(k)+'\n'+str(l.get_item_rank())+'\n' for i,j,k,l in zip(self.category_list, award_words, unique_words, award_related_word)]))
#         
#     output_file = '{}_testing_award_related_name.txt'.format(data_year)
#     with open(output_file, 'w', encoding='utf-8') as open_file:
#         open_file.write('\n'.join([str(i)+'\n'+str(j)+'\n'+str(k)+'\n'+str(l.get_item_rank())+'\n' for i,j,k,l in zip(self.category_list, award_words, unique_words, award_related_name)]))
# =============================================================================
        
    
        
        
    
# =============================================================================
#     for award_token_i, award_i in zip(award_spacy_token_list, self.category_list):
#         #print(award_i)
#         word_groups = []
#         cur_words = ''
#         for token_i in award_token_i:
#             if token_i.is_stop or not re.search('[a-z]', token_i.text):
#                 if cur_words:
#                     word_groups.append(cur_words)
#                     cur_words = ''
#             else:
#                 if cur_words:
#                     cur_words = cur_words + ' ' + token_i.text
#                 else:
#                     cur_words = token_i.text
#             #print({'text':token_i.text, 'lemma':token_i.lemma_, 'pos':token_i.pos_, 'tag':token_i.tag_, 'dep':token_i.dep_,
#             #                                'shape':token_i.shape_, 'alpha':token_i.is_alpha, 'stop':token_i.is_stop})
#         #print()
#         if cur_words:
#             word_groups.append(cur_words)
#         
#         print(word_groups)
# =============================================================================


    
# =============================================================================
#     def print_check_table(check_table):
#         print_list = []
#         for key_i in check_table:
#             val_i = check_table[key_i]
#             if type(val_i) == dict:
#                 for sublist_i in print_check_table(val_i):
#                     print_list.append([key_i]+sublist_i)
#             elif type(val_i) == int:
#                 print_list.append([key_i,val_i])
#             else:
#                 assert False, '{} {}'.format(type(val_i), val_i)
#         return print_list
#     
#     award_check_table_print = print_check_table(award_word_check_table)
#     output_file = '{}_testing_award_split_t1.txt'.format(data_year)
#     with open(output_file, 'w', encoding='utf-8') as open_file:
#         open_file.write('\n'.join([str(i[:-1])+' '+self.category_list[i[-1]] for i in award_check_table_print]))
# =============================================================================
                
    
        
# =============================================================================
#     for word_i in award_word_check_list:
#         all_related_words = set()
#         for unique_group_i in helper_unique_word_list:
#             if word_i in unique_group_i[0] or word_i in unique_group_i[1]:
#                 for related_word_i in unique_group_i[0]:
#                     all_related_words.add(related_word_i)
#                 for related_word_i in unique_group_i[1]:
#                     all_related_words.add(related_word_i)
#         print(word_i, len(all_related_words))
#         print(all_related_words)
#         print()
# =============================================================================
    
    
    
# =============================================================================
#     def build_unique_word_table(unique_words, check_list):
#         if check_list:
#             cur_check_word = check_list[0]
#             pos_check_group_list = []
#             neg_check_group_list = []
#             for unique_words_group_i in unique_words:
#                 if cur_check_word in unique_words_group_i[0]:
#                     pos_check_group_list.append(unique_words_group_i)
#                 elif cur_check_word in unique_words_group_i[1]:
#                     neg_check_group_list.append(unique_words_group_i)
#                 else:
#                     pos_check_group_list.append(unique_words_group_i)
#                     neg_check_group_list.append(unique_words_group_i)
#             cur_check_table = {True: build_unique_word_table(pos_check_group_list, check_list[1:]),
#                                False: build_unique_word_table(neg_check_group_list, check_list[1:]),}
# =============================================================================



    