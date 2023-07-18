# Modified WebCrawler class to include link following

import requests
from bs4 import BeautifulSoup
import html2text
import spacy
import concurrent.futures
import yaml
import sqlite3
from sqlite3 import Error
from gensim.summarization import summarize
from transformers import BartTokenizer, BartForConditionalGeneration
import time

class WebCrawler:
    def __init__(self, start_url, crawl_time, db_file, depth, max_pages):
        # Load the BART model
        self.model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
        self.tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')

        self.start_url = start_url
        self.crawl_time = crawl_time
        self.database = db_file
        self.depth = depth
        self.max_pages = max_pages
        self.conn = self.create_connection(self.database)


    def summarize_with_bart(self, text):
        # Tokenize the text
        inputs = self.tokenizer.encode(text, return_tensors='pt')

        # Generate a summary
        summary_ids = self.model.generate(inputs, num_beams=4, max_length=100, early_stopping=True)
        summary = self.tokenizer.decode(summary_ids[0])

        return summary

    def get_page_content(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except (requests.RequestException, ValueError):
            print("Network or URL error occurred.")
            return None
        #print(response.content)
        return response.content


    def parse_html(self, content):
        return BeautifulSoup(content, 'html.parser')

    def extract_text(self, soup):
        for script in soup(["script", "style"]):
            script.decompose()
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        converter.ignore_images = True
        text = converter.handle(soup.prettify())
        return text

    def extract_entities(self, text):
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)
        return conn

    def insert_link(self, link):
        try:
            sql = ''' INSERT INTO links(url,summary)
                      VALUES(?,?) '''
            cur = self.conn.cursor()
            cur.execute(sql, link)
            self.conn.commit()  # Commit changes to the database
            print(sql)
            return cur.lastrowid
        except Error as e:
            print(e)

    def load_keywords(self, yaml_file):
        with open(yaml_file, 'r') as file:
            keywords = yaml.safe_load(file)
        return keywords

    def get_links(self, soup):
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/wiki/') and ':' not in href:
                full_link = f"https://en.wikipedia.org{href}"
                if full_link not in links:
                    links.append(full_link)
        return links

    def scrape_url(self, url, keywords, depth=0):
        content = self.get_page_content(url)
        if content:
            soup = self.parse_html(content)
            text = self.extract_text(soup)
            if keywords:  # If keywords list is not empty
                entities = self.extract_entities(text)
                for entity, label in entities:
                    if entity in keywords:
                        summary = summarize(text)
                        link = (url, summary)
                        self.insert_link(link)
                        break
            else:  # If keywords list is empty
                summary = summarize(text)
                print(summary)
                link = (url, summary)
                self.insert_link(link)

            if depth < self.depth:
                links = self.get_links(soup)
                return links

    def run(self):
        sql_create_links_table = """ CREATE TABLE IF NOT EXISTS links (
                                            id integer PRIMARY KEY,
                                            url text NOT NULL,
                                            summary text
                                        ); """
        if self.conn is not None:
            self.create_table(sql_create_links_table)
        else:
            print("Error! cannot create the database connection.")

        keywords = self.load_keywords('keywords.yaml')

        visited = set()
        to_visit = [(self.start_url, 0)]
        start_time = time.time()

        while to_visit and len(visited) < self.max_pages and time.time() - start_time < self.crawl_time:
            current_url, current_depth = to_visit.pop(0)
            if current_url not in visited and current_depth <= self.depth:
                visited.add(current_url)
                print(f"Visiting: {current_url}")
                new_links = self.scrape_url(current_url, keywords, current_depth)
                if new_links:
                    for link in new_links:
                        if isinstance(link, list):  # If link is actually a list of links
                            for sublink in link:  # Loop through the sublinks
                                to_visit.append((sublink, current_depth + 1))
                        else:  # If link is actually a single link
                            to_visit.append((link, current_depth + 1))

            time.sleep(1)  # Wait for a second before the next round of scraping

    def create_table(self, create_table_sql):
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)
