import os
import requests
import time

from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

ALL_TABLES_URL = 'https://data.stat.gov.lv/api/v1/lv/OSP_PUB?query=*&filter=*'
TABLE_URL_BASE = 'https://data.stat.gov.lv/pxweb/lv/OSP_PUB/START__'

class OspGuiAnalyzer:

    def __init__(self, table_limit = 3, sleep_time = 2):
        self.tables_read = 0
        self.table_limit = table_limit
        self.sleep_time = sleep_time

    def read_metadata(self):
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

            print('Read table (', TABLE_URL_BASE + url_ending, ')...')

            try:
                table_response = requests.get(TABLE_URL_BASE + url_ending)
                requestSuccessful = True
            except requests.exceptions as errh:
                print('Failed reading the table page: ', errh)

            if not requestSuccessful:
                continue

            table_page_html = BeautifulSoup(table_response.text, 'html.parser')
            metadata_link = table_page_html.find('a', text='Metadati')

            if metadata_link is None:
                print ('Warning: Did not find metadata for', TABLE_URL_BASE + url_ending, '. Skipping.')
                continue

            try:
                metadata_response = requests.get(metadata_link['href'])
                requestSuccessful = True
            except requests.exceptions as errh:
                print('Failed reading the metadata page: ', errh)
            except Exception as err:
                print('Failed reading the metadata page: ', err)

            if not requestSuccessful:
                continue

            print('Read metadata (' , metadata_link['href'], ')...')

            metadata_filename = url_ending.replace('/', '__') + '.html'
            path = os.path.join('outputs/metadata_pages', metadata_filename)
            with open(path, 'wb') as f:
                f.write(metadata_response.content)

            print('Saved metadata HTML file ', i+1, '/', min(self.table_limit, len(self.tables)), ': ', metadata_filename)


    def analyze_metadata(self):

        section_length_data = []
        
        for filename in os.listdir('outputs/metadata_pages'):
            if filename.endswith('.html'):
                file_path = os.path.join('outputs/metadata_pages', filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    print(filename)
                    metadata_page = BeautifulSoup(f.read(), 'html.parser')
                    
                    subheaders = metadata_page.find_all('h2')

                    section_lengths = {}

                    for i in range(len(subheaders)):
                        subheader = subheaders[i]

                        if subheader.find_parents('footer'):
                            continue

                        section_text = ''

                        next_subheader = None
                        if i + 1 < len(subheaders):
                            next_subheader = subheaders[i+1]

                        section = subheader.find_next_sibling()
                        while section is not None and section != next_subheader:
                            section_text += section.get_text().strip()
                            section = section.find_next_sibling()

                        section_title = subheader.get_text().strip()
                        section_lengths[section_title] = len(section_text)
                        print ('|- Section', section_title, ": ", len(section_text))
                    
                    section_length_data.append(section_lengths)

        # Group section lengths by section title
        grouped_sections = {}
        for section_lengths in section_length_data:
            for section_title, section_length in section_lengths.items():
                if section_title not in grouped_sections:
                    grouped_sections[section_title] = []
                grouped_sections[section_title].append(section_length)

        # Create a separate histogram for each section title
        for section_title, section_lengths in grouped_sections.items():
            plt.hist(section_lengths, bins=20)
            plt.title(section_title)
            plt.xlabel('Section Length')
            plt.ylabel('Number of Pages')
            plt.show()
                
    