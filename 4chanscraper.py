from bs4 import BeautifulSoup 
import requests 
import urllib, urllib.request, json, os, datetime
from unidecode import unidecode
import os
import unicodecsv as csv

class fourchanScraper():

    def __init__(self):
        #CHANGE THESE SETTINGS!


    def scrape_board(self, board):
        html_text = requests.get('https://boards.4channel.org/{board}/').text
        soup = BeautifulSoup(html_text, 'lxml')
        threads = soup.find_all('div', class_='thread')
        for index, thread in enumerate(threads): 
            published_date = job.find('span', class_='sim-posted').text.replace(' ', '')
            if 'few' in published_date: 
                company_name = job.find('h3', class_='joblist-comp-name').text.replace(' ', '')
                skill = job.find('span', class_='srp-skills').text.replace(' ', '')
                more_info = job.header.h2.a['href']
                if unfamiliar_skill not in skill: 
                    with open(f'scraped_data/{index}.txt', 'w') as f:
                        f.write(f"Company Name: {company_name.strip()}")
                        f.write(f"Required Skills: {skill.strip()}")
                        f.write(f"More Info: {more_info}")



if __name__ == "__main__":
    scraper = fourchanScraper()
    print('What board would you like to scrape?')
    board = input('>')
    print(f'Scraping {board}')
    scraper.scrape_board('x')