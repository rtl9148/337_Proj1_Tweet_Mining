
## This code contains a helper class that counts items and has method to return an ordered list of items.
    
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
            
    def merge_counter(self, other_counter):
        self.total_count += other_counter.total_count
        for item_i in other_counter.item_count_table:
            if item_i in self.item_count_table:
                self.item_count_table[item_i] += other_counter.item_count_table[item_i]
            else:
                self.item_count_table[item_i] = other_counter.item_count_table[item_i]
            
            
