import requests
from bs4 import BeautifulSoup
import html2text
import spacy

def get_page_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    return None

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

def main():
    url = "https://en.wikipedia.org/wiki/OpenAI"
    content = get_page_content(url)

    if content:
        soup = parse_html(content)
        text = extract_text(soup)
        entities = extract_entities(text)

        for entity, label in entities:
            print(f"{entity} ({label})")

if __name__ == "__main__":
    main()