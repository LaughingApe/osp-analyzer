import sys
import os
import time
import json

from pyscbwrapper import SCB

class OspApiAnalyzer:

    def __init__(self):
        self.tables_read = 0
        self.table_limit = 150
        self.sleep_time = 2
        
    def __init__(self, table_limit, sleep_time):
        self.tables_read = 0
        self.table_limit = table_limit
        self.sleep_time = sleep_time
    
    def read_categories(self):
        
        scb = SCB('en')
        self.categories = scb.get_data() # categories

        print(self.categories)

        for i in range(len(self.categories)):
            if self.tables_read >= OspApiAnalyzer.table_limit:
                break
            time.sleep(self.sleep_time)
            scb = SCB('en', self.categories[i]['id'])
            self.categories[i]['subcategories'] = scb.get_data() # POP

            for j in range(len(self.categories[i]['subcategories'])):
                if self.tables_read >= OspApiAnalyzer.table_limit:
                    break
                time.sleep(self.sleep_time)
                scb = SCB('en', self.categories[i]['id'], self.categories[i]['subcategories'][j]['id'])
                self.categories[i]['subcategories'][j]['subcategories'] = scb.get_data() # POP/IR

                for k in range(len(self.categories[i]['subcategories'][j]['subcategories'])):
                    if self.tables_read >= OspApiAnalyzer.table_limit:
                        break
                    time.sleep(self.sleep_time)
                    scb = SCB('en', self.categories[i]['id'], self.categories[i]['subcategories'][j]['id'], self.categories[i]['subcategories'][j]['subcategories'][k]['id'])
                    self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'] = scb.get_data()  # POP/IR/IRE

                    for m in range(len(self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'])):
                        if self.tables_read >= OspApiAnalyzer.table_limit:
                            break
                        time.sleep(self.sleep_time)
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

                        cat1 = self.categories[i]['id']
                        cat2 = self.categories[i]['subcategories'][j]['id']
                        cat3 = self.categories[i]['subcategories'][j]['subcategories'][k]['id']
                        cat4 = self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'][m]['id']
                        table_path = cat1 + '-' + cat2 + '-' + cat3 + '-' + cat4
                        
                        if os.path.isfile('outputs/tables' + table_path):
                            print ('Warning! File ', table_path, ' already exists and will be rewritten.')

                        path = os.path.join('outputs/tables', table_path + '.json')
                        with open(path, 'w') as f:
                            json.dump(self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'][m]['table'], f, indent=4, ensure_ascii=False)
                        
                        table_counter += 1
                        print('Printed ', table_counter, '/', self.table_limit, ' tables (', table_path ,')')

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

                        cat1 = self.categories[i]['id']
                        cat2 = self.categories[i]['subcategories'][j]['id']
                        cat3 = self.categories[i]['subcategories'][j]['subcategories'][k]['id']
                        cat4 = self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'][m]['id']
                        table_path = cat1 + '-' + cat2 + '-' + cat3 + '-' + cat4
                        
                        if os.path.isfile('outputs/tables' + table_path):
                            print ('Warning! File ', table_path, ' already exists and will be rewritten.')

                        path = os.path.join('outputs/tables', table_path + '.json')                        
                        with open(path, 'w', encoding='utf-8') as f:
                            json.dump(self.categories[i]['subcategories'][j]['subcategories'][k]['subcategories'][m], f, indent=4, ensure_ascii=False)
                        
                        table_counter += 1
                        print('Printed ', table_counter, '/', self.table_limit, ' tables with extra info (', table_path ,')')
    
    def read_tables_from_file(self):
        directory = 'outputs/tables'
        self.tables = []

        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                with open(os.path.join(directory, filename), "r") as f:
                    json_data = json.load(f)
                    self.tables.append(json_data)

    def evaluate_metadata(self):
        infofile_cnt = 0
        updated_cnt = 0
        label_cnt = 0
        source_cnt = 0
        sum_of_lengths = 0

        for table in self.tables:
            (infofile_present, updated_present, label_present, source_present, label_length) = self.evaluate_metadata_of_table(table)
            infofile_cnt += 1 if infofile_present else 0
            updated_cnt += 1 if updated_present else 0
            label_cnt += 1 if label_present else 0
            source_cnt += 1 if source_present else 0
            sum_of_lengths += label_length

        print('Stats for read tables.')
        print('Infofile field provided: ', infofile_cnt, '/', len(self.tables))
        print('Updated field provided: ', updated_cnt, '/', len(self.tables))
        print('Label field provided: ', label_cnt, '/', len(self.tables))
        print('Source field provided: ', source_cnt, '/', len(self.tables))
        print('Average label length: ', sum_of_lengths / len(self.tables))
        

    def evaluate_metadata_of_table(self, table):
        # Extract the metadata from the table
        metadata = table["table"]["metadata"][0]

        # Check if each metadata field is present and not empty
        infofile_present = "infofile" in metadata and metadata["infofile"]
        updated_present = "updated" in metadata and metadata["updated"]
        label_present = "label" in metadata and metadata["label"]
        source_present = "source" in metadata and metadata["source"]

        # Get the length of the label
        label_length = len(metadata["label"])

        # Return the results as a tuple
        return (infofile_present, updated_present, label_present, source_present, label_length)

