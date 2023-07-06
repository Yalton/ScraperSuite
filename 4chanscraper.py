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
import math
import time
import os

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


class fourchanScraper():

    def __init__(self):
        print("gingus")
        #CHANGE THESE SETTINGS!
 
    def scrape_board(self, board: str):

        start_time = time.process_time()
        url = f"https://boards.4channel.org/{board}/"  # Replace with the URL of the page you want to scrape
        

        print(url)

        #object of Options class
        c = Options()
        #passing headless parameter
        #c.add_argument("--headless")


        # Define the path to the chromedriver
        driver_path = "/opt/chromedriver/chromedriver"

        # Initialize the webdriver
        driver = webdriver.Chrome(service=Service(driver_path), options=c)

        # Navigate to the url
        driver.get(url)

        #time.sleep(5)  # You may need to adjust the waiting time based on the website's loading time

        wait = WebDriverWait(driver, 10)

        # Locate the "All" button using the CSS selector
        all_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.depagelink")))

        # Click the "All" button
        all_button.click()

        # Wait for the new content to load (adjust the waiting time as needed)
        time.sleep(5)  # You may need to adjust the waiting time based on the website's loading time

        # Wait for the expand buttons to load
        wait = WebDriverWait(driver, 30)
        expand_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img.extButton.expbtn")))

        #expand_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img.extButton.expbtn")))

        # Click all expand buttons
        for button in expand_buttons:
            button.click()
            time.sleep(1)

        time.sleep(5)
        # Get the resulting HTML content
        html_content = driver.page_source

        driver.quit()

        # Continue processing the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        #response = requests.get(url)
        #html_content = response.text

        soup = BeautifulSoup(html_content, "html.parser")

        # Create a directory to store the downloaded images and messages

        # x = datetime.datetime.now().strftime("%X")
        # x.strftime("%X")
        board_dir = board + "__" +datetime.datetime.now().strftime("%m-%d-%y")

        if not os.path.exists(board_dir):
            os.makedirs(board_dir)


        threads_directory = os.path.join(board_dir, "threads")
        if not os.path.exists(threads_directory):
                os.makedirs(threads_directory)

        # thread_directory = os.path.join("threads", thread_id)
        # if not os.path.exists(thread_directory):
        #         os.makedirs(thread_directory)

        threads = soup.find_all("div", class_="thread")

        for thread in threads:
            thread_id = thread["id"].replace("t", "")

            # Create a directory for each thread
            thread_directory = os.path.join(threads_directory, thread_id)
            if not os.path.exists(thread_directory):
                os.makedirs(thread_directory)

            # Save all messages in the current thread to a text file
            post_containers = thread.find_all("div", class_="postContainer")
            with open(os.path.join(thread_directory, "messages.txt"), "w", encoding="utf-8") as message_file:
                for container in post_containers:
                    post_id = container["id"].replace("pc", "")
                    subject = container.find("span", class_="subject")
                    message = container.find("blockquote", class_="postMessage")

                    if subject:
                        message_file.write(f"Subject: {subject.get_text(strip=True)}\n")
                    message_file.write(f"Post ID: {post_id}\n")
                    message_file.write(f"Message: {message.get_text(strip=True)}\n\n")

            # Create a directory for images in the current thread
            image_directory = os.path.join(thread_directory, "images")
            if not os.path.exists(image_directory):
                os.makedirs(image_directory)

            # Find all the image URLs in the current thread
            images = thread.find_all("a", class_="fileThumb")

            for image in images:
                image_url = image["href"]
                if image_url.startswith("//"):
                    image_url = "https:" + image_url
                filename = os.path.join(image_directory, os.path.basename(image_url))

                # Download the image and save it in the corresponding thread directory
                urllib.request.urlretrieve(image_url, filename)
                print(f"Downloaded {filename}")
        
        end_time = time.process_time()
        with open(os.path.join(threads_directory, "log.txt"), "w", encoding="utf-8") as log_file:
            size_in_bytes = get_directory_size(threads_directory)
            log_file.write(f"Size of Scrape: {convert_size(size_in_bytes)}\n")
            log_file.write(f"Time Elapsed: {(end_time - start_time) * 1000} ms")
        

if __name__ == "__main__":

    # Create the parser
    parser = argparse.ArgumentParser(description="This is a script for scraping 4Chan")

    # Add the arguments
    parser.add_argument("-b", "--board", type=str, required=True, help="The board to scrape")

    # Parse the arguments
    args = parser.parse_args()

    scraper = fourchanScraper()
    # print('What board would you like to scrape?')
    # board = input('>')
    print(f'Scraping {args.board}')
    scraper.scrape_board(f'{args.board}')



      # response = requests.get(url)
        # html_content = response.text

        # soup = BeautifulSoup(html_content, "html.parser")

        # # Create a directory to store the downloaded images and messages
        # if not os.path.exists("threads"):
        #     os.makedirs("threads")

        # threads = soup.find_all("div", class_="thread")

        # for thread in threads:
        #     thread_id = thread["id"].replace("t", "")

        #     # Create a directory for each thread
        #     thread_directory = os.path.join("threads", thread_id)
        #     if not os.path.exists(thread_directory):
        #         os.makedirs(thread_directory)

        #     # Save all messages in the current thread to a text file
        #     messages = thread.find_all("blockquote", class_="postMessage")
        #     with open(os.path.join(thread_directory, "messages.txt"), "w", encoding="utf-8") as message_file:
        #         for message in messages:
        #             message_file.write(message.get_text(strip=True) + "\n")

        #     # Create a directory for images in the current thread
        #     image_directory = os.path.join(thread_directory, "images")
        #     if not os.path.exists(image_directory):
        #         os.makedirs(image_directory)

        #     # Find all the image URLs in the current thread
        #     images = thread.find_all("a", class_="fileThumb")

        #     for image in images:
        #         image_url = image["href"]
        #         if image_url.startswith("//"):
        #             image_url = "https:" + image_url
        #         filename = os.path.join(image_directory, os.path.basename(image_url))

        #         # Download the image and save it in the corresponding thread directory
        #         urllib.request.urlretrieve(image_url, filename)
        #         print(f"Downloaded {filename}")
        
        # # Replace this with the URL you want to scrape
        # url = f"https://boards.4channel.org/{board}/"

        # response = requests.get(url)
        # soup = BeautifulSoup(response.text, 'html.parser')

        # # Find all post containers
        # post_containers = soup.find_all('div', class_='postContainer')
        # print("Scraping", url)



        # threads = soup.find_all("div", class_="thread")
        
        # for thread in threads:
        #     thread_id = thread["id"].replace("t", "")
        #     # Extract information from each post
        #     for post_container in post_containers:
        #         post_id = post_container['id'][2:]
        #         post = post_container.find('div', class_='post')
        #         post_datetime = post.find('span', class_='dateTime').text
        #         post_message = post.find('blockquote', class_='postMessage').text

        #         # Extract file information if available
        #         file_div = post.find('div', class_='file')
        #         if file_div:
        #             file_text = file_div.find('div', class_='fileText').text
        #         else:
        #             file_text = None

        #         print(f"Post ID: {post_id}")
        #         print(f"Date Time: {post_datetime}")
        #         print(f"Message: {post_message}")
        #         print(f"File Info: {file_text}\n")

        # html_text = requests.get('https://boards.4channel.org/{board}/').text
        # soup = BeautifulSoup(html_text, 'lxml')
        # 
        # 
        #     posts = thread.find_all('div', class_='postContainer')
        #     for post_index, posts in enumerate(posts): 
                
        #         company_name = job.find('h3', class_='joblist-comp-name').text.replace(' ', '')
        #         skill = job.find('span', class_='srp-skills').text.replace(' ', '')
        #         more_info = job.header.h2.a['href']
        #         if unfamiliar_skill not in skill: 
        #             with open(f'scraped_data/{board}/thread_{index}.txt', 'w') as f:
        #                 f.write(f"Company Name: {company_name.strip()}")
        #                 f.write(f"Required Skills: {skill.strip()}")
        #                 f.write(f"More Info: {more_info}")
        # Wait for the expand buttons to load