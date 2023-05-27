import os
import sys
import requests
import time
from datetime import datetime, date

from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

ALL_TABLES_URL = 'https://data.stat.gov.lv/api/v1/lv/OSP_PUB?query=*&filter=*'
TABLE_URL_BASE = 'https://data.stat.gov.lv/pxweb/lv/OSP_PUB/START__'
DATASET_HTML_DIR = 'outputs/dataset_pages'
DIAGRAM_DIR = 'outputs/dataset_diagrams'
EMPTY_FIELD_LOG = 'empty_fields.txt'
LIST_FILE = 'list.txt'

class OspDateAnalyzer:

    def __init__(self, table_limit = 3, sleep_time = 2):
        self.tables_read = 0
        self.table_limit = table_limit
        self.sleep_time = sleep_time

    def read_date_pages(self):
        response = requests.get(ALL_TABLES_URL)

        if response.status_code != 200:
            print('Error:', response.status_code)
            return
        self.tables = response.json()

        for i in range(len(self.tables)):
            if i >= self.table_limit:
                break

            time.sleep(self.sleep_time)

            url_ending = self.tables[i]['path'][1:]
            url_ending = url_ending.replace('/', '__')
            url_ending += '/' + self.tables[i]['id']

            self.download_dataset_page(url_ending)
            print('Saved metadata HTML file ', i+1, '/', min(self.table_limit, len(self.tables)), ': ', url_ending.replace('/', '__') + '.html', end='\r')

    def download_dataset_page(self, url_ending):
        try:
            dataset_response = requests.get(TABLE_URL_BASE + url_ending)
            requestSuccessful = True
        except requests.exceptions as errh:
            print('Failed reading the table page: ', errh)
            return False
        
        dataset_filename = url_ending.replace('/', '__') + '.html'
        path = os.path.join(DATASET_HTML_DIR, dataset_filename)
        with open(path, 'wb') as f:
            f.write(dataset_response.content)
        return True

    def analyze_date_data(self):

        try:
            os.remove(os.path.join(DIAGRAM_DIR, EMPTY_FIELD_LOG))
        except:
            pass

        date_data = []
        filenames = []

        files = os.listdir(DATASET_HTML_DIR)
        
        total_working_pages = 0

        for filename in files:
            if filename.endswith('.html'):
                file_path = os.path.join(DATASET_HTML_DIR, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_working_pages += 1
                    dataset_page = BeautifulSoup(f.read(), 'html.parser')

                    update_date = self.extract_date(dataset_page)
                    
                    if update_date != None:
                        days_from_today = (date.today()-update_date).days
                        date_data.append(days_from_today // 7)
                        filenames.append(filename)
                    else:
                        with open(os.path.join(DIAGRAM_DIR, EMPTY_FIELD_LOG), 'a', encoding='utf-8') as f:
                            original_stdout = sys.stdout
                            sys.stdout = f 
                            print ('No updated field for', filename)
                            sys.stdout = original_stdout

                    print('Processed', len(filenames), '/', len(files), 'HTML metadata files', end='\r')
        
        self.generate_list(zip(date_data, filenames))
        self.generate_charts(date_data)

    def extract_date(self, dataset_page):
        date_element = dataset_page.find('div', class_='information_lastupdated_value')
        if date_element == None:
            return None
        date_string = date_element.text.strip()
        return datetime.strptime(date_string, '%d.%m.%Y').date()
    
    def generate_list(self, data_list):
        sorted_list = sorted(data_list)
        with open(os.path.join(DIAGRAM_DIR, LIST_FILE), 'w', encoding='utf-8') as f:
            original_stdout = sys.stdout
            sys.stdout = f 
            
            for item in sorted_list:
                print(item[0], 'weeks since last update for', item[1])

            sys.stdout = original_stdout

    def generate_charts(self, date_data):

        plt.hist(date_data, bins=40, edgecolor='black', alpha=0.7)
        plt.title('Datu kopu aktualitāte')
        plt.xlabel('Nedēļas kopš pēdējās datu atjaunošanas')
        plt.ylabel('Datu kopu skaits')
        plt.grid(True, axis='y')  
        x_ticks = plt.xticks()[0]
        plt.xticks(x_ticks, [int(tick) if tick.is_integer() else '' for tick in x_ticks])

        plt.xlim(0, max(date_data) + 5)  

        plt.tight_layout()
        plt.savefig(DIAGRAM_DIR + '/dates.pdf', format='pdf')
        plt.close()

