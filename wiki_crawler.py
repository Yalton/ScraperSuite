import requests
from bs4 import BeautifulSoup
import re
import time

def get_page(url):
    try:
        page = requests.get(url)
        if page.status_code == 200:
            return page.content
        else:
            return None
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None

def get_links(soup):
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/wiki/') and ':' not in href:
            full_link = f"https://en.wikipedia.org{href}"
            if full_link not in links:
                links.append(full_link)
    return links

def get_title(soup):
    title_tag = soup.find('h1', {'id': 'firstHeading'})
    return title_tag.text if title_tag else "Unknown"

def web_crawler(start_url, depth, max_pages):
    visited = set()
    to_visit = [(start_url, 0)]

    while to_visit and len(visited) < max_pages:
        current_url, current_depth = to_visit.pop(0)
        if current_url not in visited and current_depth <= depth:
            visited.add(current_url)
            print(f"Visiting: {current_url}")
            page_content = get_page(current_url)
            if page_content:
                soup = BeautifulSoup(page_content, 'html.parser')
                title = get_title(soup)
                print(f"Title: {title}")

                if current_depth < depth:
                    new_links = get_links(soup)
                    for link in new_links:
                        to_visit.append((link, current_depth + 1))

            time.sleep(1)

    print("Crawling complete!")

if __name__ == "__main__":
    start_url = "https://en.wikipedia.org/wiki/Web_scraping"
    depth = 2
    max_pages = 50
    web_crawler(start_url, depth, max_pages)