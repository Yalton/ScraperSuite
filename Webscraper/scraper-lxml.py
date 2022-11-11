from bs4 import BeautifulSoup


with open('home.html', 'r') as html_file:
    content = html_file.read()
    # print(content)
    soup = BeautifulSoup(content, "lxml")
    courses_html_tags = soup.find_all('a')
    for course in courses_html_tags:
        print(course.text)
