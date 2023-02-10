from bs4 import BeautifulSoup 
import requests 

print('Put some skill that you are not familiar with')
unfamiliar_skill = input('>')
print(f'Filtering out {unfamiliar_skill}')

def find_jobs():
    html_text = requests.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=python&txtLocation=').text
    soup = BeautifulSoup(html_text, 'lxml')
    jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')

    for index, job in enumerate(jobs): 
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
        
        
if __name__ == '__main__': 
    find_jobs()