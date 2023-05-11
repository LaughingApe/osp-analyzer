import sys
import os
import time
import json

from pyscbwrapper import SCB
from matplotlib import pyplot


class OSPReader:

    table_limit = 2

    def __init__(self):
        self.tables_read = 0
    
    def read_categories(self):
        
        scb = SCB('en')
        self.categories = scb.get_data() # categories

        print(self.categories)

        for i in range(len(self.categories)):
            if self.tables_read >= OSPReader.table_limit:
                break
            time.sleep(1)
            scb = SCB('en', self.categories[i]['id'])
            self.categories[i]['subcategories'] = scb.get_data() # POP

            for j in range(len(self.categories[i]['subcategories'])):
                if self.tables_read >= OSPReader.table_limit:
                    break
                time.sleep(1)
                scb = SCB('en', self.categories[i]['id'], self.categories[i]['subcategories'][j]['id'])
                self.categories[i]['subcategories'][j]['subcategories'] = scb.get_data() # POP/IR

                for k in range(len(self.categories[i]['subcategories'][j]['subcategories'])):
                    if self.tables_read >= OSPReader.table_limit:
                        break
                    time.sleep(1)
                    scb = SCB('en', self.categories[i]['id'], self.categories[i]['subcategories'][j]['id'], self.categories[i]['subcategories'][j]['subcategories'][k]['id'])
                    self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'] = scb.get_data()  # POP/IR/IRE

                    for m in range(len(self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'])):
                        if self.tables_read >= OSPReader.table_limit:
                            break
                        time.sleep(1)
                        scb = SCB('en', self.categories[i]['id'], self.categories[i]['subcategories'][j]['id'], self.categories[i]['subcategories'][j]['subcategories'][k]['id'], self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'][m]['id'])
                        self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'][m]['table'] = scb.get_data()  # POP/IR/IRE/IRE010
                        self.tables_read += 1
                        print('Read ', self.tables_read, '/', self.table_limit, ' tables')

        # print(self.categories)
    
    def print_categories_tables(self):
        table_counter = 0

        for i in range(len(self.categories)):
            if not 'subcategories' in self.categories[i]:
                continue
            for j in range(len(self.categories[i]['subcategories'])):
                if not 'subcategories' in self.categories[i]['subcategories'][j]:
                    continue
                for k in range(len(self.categories[i]['subcategories'][j]['subcategories'])):
                    if not 'subcategories' in self.categories[i]['subcategories'][j]['subcategories'][k]:
                        continue
                    for m in range(len(self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'])):
                        if not 'table' in self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'][m]:
                            continue

                        path = os.path.join('outputs/tables', self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'][m]['id'] + '.json')
                        with open(path, 'w') as f:
                            json.dump(self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'][m]['table'], f, indent=4, ensure_ascii=False)
                        
                        table_counter += 1
                        print('Printed ', table_counter, '/', self.table_limit, ' tables')

    def print_categories_tables_with_extra_info(self):
        table_counter = 0

        for i in range(len(self.categories)):
            if not 'subcategories' in self.categories[i]:
                continue
            for j in range(len(self.categories[i]['subcategories'])):
                if not 'subcategories' in self.categories[i]['subcategories'][j]:
                    continue
                for k in range(len(self.categories[i]['subcategories'][j]['subcategories'])):
                    if not 'subcategories' in self.categories[i]['subcategories'][j]['subcategories'][k]:
                        continue
                    for m in range(len(self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'])):
                        if not 'table' in self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'][m]:
                            continue

                        path = os.path.join('outputs/tables', self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'][m]['id'] + '.json')
                        with open(path, 'w', encoding='utf-8') as f:
                            json.dump(self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'][m], f, indent=4, ensure_ascii=False)
                        
                        table_counter += 1
                        print('Printed ', table_counter, '/', self.table_limit, ' tables with extra info')
    
    def read_tables_from_file(self):
        directory = 'outputs/tables'
        self.tables = []

        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                with open(os.path.join(directory, filename), "r") as f:
                    json_data = json.load(f)
                    self.tables.append(json_data)

