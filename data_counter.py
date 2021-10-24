

class Item_Counter_2L():
    def __init__(self):
        self.total_count = 0
        self.item_count_table = {}
        self.item_total_count = {}
    
    def get_total_count(self, target_item = ''):
        return self.item_total_count[target_item] if target_item in self.item_total_count else self.total_count
    
    def get_count_table(self):
        return self.item_count_table
        
    def count_item(self, item_in, subitem_in, add_count = 1):
        self.total_count += add_count
        if item_in in self.item_count_table:
            self.item_total_count[item_in] += add_count
        else:
            self.item_total_count[item_in] = add_count
            self.item_count_table[item_in] = Item_Counter()
        self.item_count_table[item_in].count_item(subitem_in, add_count)
    
    def get_item_rank(self, reverse_order = True):
        item_rank_list = []
        for item_i in self.item_count_table:
            item_rank_list.append((self.item_total_count[item_i], item_i, self.item_count_table[item_i].get_item_rank()))
        item_rank_list.sort(reverse=reverse_order)
        return item_rank_list
    
    
class Item_Counter():
    def __init__(self):
        self.total_count = 0
        self.item_count_table = {}
    
    def get_total_count(self):
        return self.total_count
    
    def get_count_table(self):
        return self.item_count_table
    
    def get_item_rank(self, reverse_order = True):
        item_rank_list = [(self.item_count_table[i], i) for i in self.item_count_table]
        item_rank_list.sort(reverse=reverse_order)
        return item_rank_list
    
    def count_item(self, item_in, add_count = 1):
        self.total_count += add_count
        if item_in in self.item_count_table:
            self.item_count_table[item_in] += add_count
        else:
            self.item_count_table[item_in] = add_count
            
