

import json, os, re

if __name__ == '__main__':
    data_file = 'gg2015.json'
    with open(data_file,'r') as open_file:
        data_entries = json.load(open_file)
    data_lines = [i['text'] for i in data_entries]
    check_list = ['foreign','win']
    extract_line = '\"((?:[A-Z]+[a-z]*[ ]?)+)\"'
    extract_table = {}
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
                    if key_i in count_table[key_normal]:
                        count_table[key_normal][key_i] += 1
                    else:
                        count_table[key_normal][key_i] = 1
                else:
                    count_table[key_normal] = {key_i: 1}
    print(count_table)
    max_key = ''
    max_count = 0
    for key_i in count_table:
        cur_count = 0
        cur_max_key = ''
        cur_max_count = 0
        for key_j in count_table[key_i]:
            cur_count += count_table[key_i][key_j]
            if count_table[key_i][key_j]>cur_max_count:
                cur_max_count = count_table[key_i][key_j]
                cur_max_key = key_j
        if cur_count>max_count:
            max_count = cur_count
            max_key = cur_max_key
    print(max_key)
        

