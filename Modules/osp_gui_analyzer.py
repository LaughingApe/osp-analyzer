import os
import sys
import requests
import time
import re

from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

ALL_TABLES_URL = 'https://data.stat.gov.lv/api/v1/lv/OSP_PUB?query=*&filter=*'
TABLE_URL_BASE = 'https://data.stat.gov.lv/pxweb/lv/OSP_PUB/START__'
METADATA_HTML_DIR = 'outputs/metadata_pages'
METADATA_DIAGRAM_DIR = 'outputs/metadata_diagrams'
STATS_FILE = 'missing_sections.txt'

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

            self.download_metadata_page(table_response, url_ending)
            print('Saved metadata HTML file ', i+1, '/', min(self.table_limit, len(self.tables)), ': ', url_ending.replace('/', '__') + '.html')

    def download_metadata_page(self, table_response, url_ending):
        table_page_html = BeautifulSoup(table_response.text, 'html.parser')
        metadata_link = table_page_html.find('a', text='Metadati')

        if metadata_link is None:
            print ('Warning: Did not find metadata for', TABLE_URL_BASE + url_ending, '. Skipping.')
            return

        try:
            metadata_response = requests.get(metadata_link['href'])
            requestSuccessful = True
        except requests.exceptions as errh:
            print('Failed reading the metadata page: ', errh)
        except Exception as err:
            print('Failed reading the metadata page: ', err)

        if not requestSuccessful:
            return

        print('Read metadata (' , metadata_link['href'], ')...')

        metadata_filename = url_ending.replace('/', '__') + '.html'
        path = os.path.join(METADATA_HTML_DIR, metadata_filename)
        with open(path, 'wb') as f:
            f.write(metadata_response.content)


    def analyze_metadata(self, subsections = False):

        try:
            os.remove(os.path.join(METADATA_DIAGRAM_DIR, STATS_FILE))
        except:
            pass

        section_length_data = []
        section_content_data = []
        section_filenames = []

        files = os.listdir(METADATA_HTML_DIR)
        
        total_working_metadata_pages = 0

        for filename in files:
            if filename.endswith('.html'):
                file_path = os.path.join(METADATA_HTML_DIR, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_working_metadata_pages += 1
                    metadata_page = BeautifulSoup(f.read(), 'html.parser')

                    section_lengths, section_contents = self.process_sections(filename, metadata_page, subsections)
                    
                    section_length_data.append(section_lengths)
                    section_content_data.append(section_contents)
                    section_filenames.append(filename)

                    print('Processed', len(section_length_data), '/', len(files), 'HTML metadata files', end='\r')
                    if len(section_lengths) < 4:
                        print('Warning: Data set', file_path, 'has', len(section_lengths), 'sections. ')
        
        # Group section lengths by section title
        grouped_sections = self.group_sections(section_length_data, total_working_metadata_pages)

        self.print_empty_sections(grouped_sections, section_length_data, section_filenames, section_content_data, subsections)
        self.generate_charts(grouped_sections)


    # Create a separate histogram for each section
    def generate_charts(self, grouped_sections):
        for section_title, section_lengths in grouped_sections.items():

            max_length = max(section_lengths)
            step = max(max_length // 20, 1)

            plt.hist(section_lengths, bins=range(0, max_length + step, step), edgecolor='black', alpha=0.7)
            plt.title(section_title)
            plt.xlabel('Sadaļas garums')
            plt.ylabel('Datu kopu skaits')
            plt.grid(True, axis='y')  
            x_ticks = plt.xticks()[0]
            plt.xticks(x_ticks, [int(tick) if tick.is_integer() else '' for tick in x_ticks])

            plt.xlim(0, max_length + step)  
            plt.tight_layout()
            plt.savefig('outputs/metadata_diagrams/' + self.get_safe_string(section_title) + '.pdf', format='pdf')
            plt.close()

    def print_empty_sections(self, grouped_sections, section_length_data, section_filenames, section_content_data, subsections):
        empty_threshold = 5 if subsections else 100 # Let's consider subsection to be empty if it has <=5 characters but large section to be empty if it has <=100

        for section in grouped_sections:
            original_stdout = sys.stdout

            try:
                os.remove(os.path.join(METADATA_DIAGRAM_DIR, self.get_safe_string(section) + '.txt'))
            except:
                pass

            with open(os.path.join(METADATA_DIAGRAM_DIR, self.get_safe_string(section) + '.txt'), 'a', encoding='utf-8') as f:
                sys.stdout = f 

                for i in range(0, len(section_length_data)):
                    if not section in section_length_data[i]:
                        print('Section "', section, '" does not exist for ', section_filenames[i])
                    elif section_length_data[i][section] <= empty_threshold:
                        print('Section "', section , '" in', section_filenames[i],'only has', section_length_data[i][section], 'characters. Content:', section_content_data[i][section])
                sys.stdout = original_stdout

    # Group section lengths by section title
    def group_sections(self, section_length_data, total_working_metadata_pages):
        grouped_sections = {}
        for section_lengths in section_length_data:
            for section_title, section_length in section_lengths.items():
                if section_title not in grouped_sections:
                    grouped_sections[section_title] = []
                grouped_sections[section_title].append(section_length)

        # Add zeros for length of non-existant sections
        for section in grouped_sections:
            for i in range(0, total_working_metadata_pages - len(grouped_sections[section])):
                grouped_sections[section].append(0)

        return grouped_sections

    def process_sections(self, filename, metadata_page, subsections):
        element_name = 'h3' if subsections else 'h2'
        subheaders = metadata_page.find_all(element_name)

        section_lengths = {}
        section_contents = {}
        
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

            # print('Length', len(section_text), ':', section_text)

            section_title = subheader.get_text().strip()
            section_lengths[section_title] = len(section_text)
            section_contents[section_title] = section_text

            # if len(section_text) <= empty_threshold:
            #     original_stdout = sys.stdout
            #     with open(os.path.join(METADATA_DIAGRAM_DIR, STATS_FILE), 'a', encoding='utf-8') as f:
            #         sys.stdout = f # Change the standard output to the file we created.
            #         print('Section "', section_title, '" might be empty (', len(section_text),') for', filename,'. Contents:', section_text)
            #         sys.stdout = original_stdout # Reset the standard output to its original value

        return section_lengths, section_contents

    def get_safe_string(self, str):
        return re.sub(r'[\W_]', '', str)
                
    