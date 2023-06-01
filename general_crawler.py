import requests
from bs4 import BeautifulSoup
import html2text
import spacy
import concurrent.futures

def get_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except (requests.RequestException, ValueError):
        print("Network or URL error occurred.")
        return None
    return response.content

def parse_html(content):
    return BeautifulSoup(content, 'html.parser')

def extract_text(soup):
    for script in soup(["script", "style"]):
        script.decompose()

    converter = html2text.HTML2Text()
    converter.ignore_links = True
    converter.ignore_images = True
    text = converter.handle(soup.prettify())
    return text

def extract_entities(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def scrape_url(url):
    content = get_page_content(url)
    if content:
        soup = parse_html(content)
        text = extract_text(soup)
        entities = extract_entities(text)

        for entity, label in entities:
            print(f"{entity} ({label})")

def main():
    urls = ["https://en.wikipedia.org/wiki/OpenAI", "https://en.wikipedia.org/wiki/Machine_learning"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(scrape_url, urls)

if __name__ == "__main__":
    main()
