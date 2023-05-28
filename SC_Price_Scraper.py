from bs4 import BeautifulSoup
import requests 
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import csv


subUrls = ["AcryliPlex%20Composite", "Agricium", "Agricium%20%28Ore%29", "Agricultural%20Supplies", "Altruciatoxin", "Aluminum", "Aluminum%20%28Ore%29", "Amioshi%20Plague", "Aphorite", "Astatine", "Atlasium", "Audio-Visual%20%Equipment", "Beryl", "Beryl%20%28Raw%29", "Bexalite", "Bexalite%20%28Raw%29", "Borase", "Borase%20%28Ore%29", "Chlorine", "Compboard", "Construction%20Materials", "Copper", "Copper%20%28Ore%29", "Corundum", "Corundum%20%28Raw%29", "Degnous", "Root", "Diamond", "Diamond%20%28Raw%29", "Diluthermex", "Distilled%20%Spirits", "Dolivine", "Dymantium", "E'tam", "Fireworks", "Fluorine", "Gold", "Gold%20%28Ore%29", "Golden%20%Medmon", "Hadanite", "%20%of%20%the%20%Woods%20%Helium", "Hephaestanite", "Hephaestanite%20%28Raw%29", "Hydrogen", "Inert%20%Materials", "Iodine", "Iron", "Iron%20%28Ore%29", "Janalite", "Laranite", "Laranite%20%28Raw%29", "Maze", "Medical%20%Supplies", "Neon", "Pitambu", "Processed%20%Food", "Prota", "Quantainium", "Quantainium%20%28Raw%29", "Quartz", "Quartz%20%28Raw%29", "Ranta%20%Dung", "Recycled%20%Material%20%Composite", "Revenant%20%Pod", "Revenant%20%Tree%20%Pollen", "SLAM", "Scrap", "Souvenirs", "Stims", "Sunset%20Berries", "Taranite", "Taranite%20%28Raw%29", "Titanium", "Titanium%20%28Ore%29", "Tungsten", "Tungsten%20%28Ore%29", "Waste", "WiDoW", "Year%20of%20the%20Rooster%20Envelope", "Zeta-Prolanide"]

for subURL in subUrls: 
    url = f"https://sc-trade.tools/commodities/{subURL}"


    options = Options()
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.cookies": 2
    })
    #passing headless parameter
    #options.add_argument("--headless")

    # Set up the Selenium WebDriver
    driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)  

    driver.delete_all_cookies()

    driver.get(url)

    time.sleep(3)

    wait = WebDriverWait(driver, 25)

    html_content = driver.page_source

    driver.quit()

    # html_content = requests.get(url).text

    soup = BeautifulSoup(html_content, "html.parser")

    with open("test.html", "w", encoding="utf-8") as out_file:
        out_file.write(html_content)

    target_divs = soup.find_all("div", class_="col-lg-6")

    csv_name = subURL.replace("%20", "")
    csv_name = csv_name.replace("%28", "")
    csv_name = csv_name.replace("%29", "")

    # Open the CSV file for writing. 'w' stands for write mode.
    with open(f"SC_CSVS/{csv_name}.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        
        print(f"Scraping {csv_name} ....")
        # Write the header row
        writer.writerow(["Purchase_Type", "Facility", "Location", "Price", "Inventory"])

        for div in target_divs: 
            purchase_type = div.find('h2', {'_ngcontent-ijb-c77': ''})
            if purchase_type is not None:
                #print(purchase_type.text)
                table = div.find('table', {'_ngcontent-ahb-c74': ''})
                if(table is not None):
                    table_rows = table.find_all('tr', class_="table-secondary")
                    for table_row in table_rows: 
                        # Find the td tags within this table row only
                        td_tags = table_row.find_all('td', {'_ngcontent-dcv-c74': ''})

                        for td in td_tags:
                            # If this td tag has an h5 tag with class 'card-title'
                            h5 = td.find('h5', {'class': 'card-title'})
                            h6 = td.find('h6')

                            if h5 and h6:
                                # Extract and print the name and location
                                facility = h5.find('a').text if h5.find('a') else ''
                                location = h6.text

                                price_tags = td.find_next_siblings('td')
                                if price_tags:
                                    price_tag = price_tags[0]
                                    price = price_tag.find('span', class_="text-success").text if price_tag.find('span', class_="text-success") else ''

                                    if len(price_tags) > 1:
                                        inventory_tag = price_tags[1]
                                        inventory = inventory_tag.text

                                # Write the row of data to the CSV file
                                writer.writerow([purchase_type.text, facility, location, price, inventory])

                        #print(facility, location, price, inventory)
                    

    print("Complete!")