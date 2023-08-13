from bs4 import BeautifulSoup 
import requests 
import argparse

import urllib, urllib.request, json, os, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import math
import time
import os

from selenium.webdriver.common.action_chains import ActionChains

from webdriver_manager.chrome import ChromeDriverManager

#driver = webdriver.Chrome(ChromeDriverManager().install())


def get_directory_size(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


class fourplebsScraper():

    def __init__(self):
        print("gingus")
        #CHANGE THESE SETTINGS!
    def scrape_board(self, board: str, pages_to_scrape: int = 1000):
        start_time = time.process_time()
        base_url = f"https://archive.4plebs.org/{board}/page/"

        MAX_RETRIES = 5

        # object of Options class
        c = Options()
        # passing headless parameter
        c.add_argument("--headless")
        c.add_argument("--window-size=1920,1080")
        c.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36")
        # c.add_experimental_option("excludeSwitches", ["enable-automation"])
        c.add_experimental_option('useAutomationExtension', False)

        # Define the path to the chromedriver
        driver_path = "/opt/chromedriver/chromedriver"


        for page_num in range(82, pages_to_scrape + 1):
            retries = 0
            
            url = f"{base_url}{page_num}/"

            print(url)


            # Initialize the webdriver
            driver = webdriver.Chrome(service=Service(driver_path), options=c)

            try: 
                driver.get(url)
            except WebDriverException:
                while retries < MAX_RETRIES:
                    try:
                        url = f"{base_url}{page_num}/"
                        driver.get(url)
                        break
                    except WebDriverException:
                        print(f"Error connecting to {url}. Retrying {retries + 1}/{MAX_RETRIES}")
                        retries += 1
                        time.sleep(5)  # sleep for 5 seconds between retries
                if retries == MAX_RETRIES:
                    print(f"Failed to scrape {url} after {MAX_RETRIES} retries.")
                    exit(1)
            

            # Wait for the expand thread buttons to load
            wait = WebDriverWait(driver, 20)  # Increase the timeout to 20 seconds
            driver.save_screenshot("screenshot.png")
            expand_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[data-function='expandThread']")))

            try: 
                # Click all expand thread buttons
                for button in expand_buttons:
                    ActionChains(driver).move_to_element(button).click(button).perform()
                    time.sleep(1)

                time.sleep(5)

                # Get the resulting HTML content
                html_content = driver.page_source

                driver.quit()

                # Continue processing the HTML content with BeautifulSoup
                soup = BeautifulSoup(html_content, "html.parser")

                board_dir = board + "__" + datetime.datetime.now().strftime("%m-%d-%y")

                if not os.path.exists(board_dir):
                    os.makedirs(board_dir)

                threads_directory = os.path.join(board_dir, "threads")
                if not os.path.exists(threads_directory):
                    os.makedirs(threads_directory)

                threads = soup.find_all("article", {"class": lambda x: x and "clearfix" in x and "thread" in x})

                print(f"Found {len(threads)} threads")

                for thread in threads:
                    thread_id = thread.get("data-thread-num")
                    if thread_id is not None:
                        thread_directory = os.path.join(threads_directory, thread_id)
                        if not os.path.exists(thread_directory):
                            os.makedirs(thread_directory)
                        
                        # Extracting and saving the content of the first post in the thread
                        first_post_text_div = thread.find("div", class_="text")
                        if first_post_text_div:
                            first_post_id = thread.find("a", attrs={"data-function": "quote"})["data-post"]
                            with open(os.path.join(thread_directory, "messages.txt"), "a", encoding="utf-8") as message_file:
                                message_file.write(f"{first_post_id}: {first_post_text_div.get_text(strip=True)}\n")

                        # Extracting and saving the content of the rest of the posts in the thread
                        posts = thread.find_all("article", class_="post")
                        for post in posts:
                            text_div = post.find("div", class_="text")
                            post_id = post.find("a", attrs={"data-function": "quote"})["data-post"]
                            if text_div:
                                with open(os.path.join(thread_directory, "messages.txt"), "a", encoding="utf-8") as message_file:
                                    message_file.write(f"{post_id}: {text_div.get_text(strip=True)}\n")

                print(f"Scraped {len(threads)} threads")
            except: 
                print("Could not Open Buttons; skipping page")
            time.sleep(2)  # Sleep for 5 seconds


        print(f"Scraped board {board} in {time.process_time() - start_time} seconds")


if __name__ == "__main__":

    # Create the parser
    parser = argparse.ArgumentParser(description="This is a script for scraping 4Chan")

    # Add the arguments
    parser.add_argument("-b", "--board", type=str, required=True, help="The board to scrape")

    # Parse the arguments
    args = parser.parse_args()

    scraper = fourplebsScraper()
    # print('What board would you like to scrape?')
    # board = input('>')
    print(f'Scraping {args.board}')
    scraper.scrape_board(f'{args.board}')

