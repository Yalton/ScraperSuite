from advanced_crawler import WebCrawler
import sqlite3

def view_data(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM links")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()

    

crawler = WebCrawler(start_url="http://lhohq.info", 
                     crawl_time=3600, 
                     db_file="my_database.db", 
                     depth = 20, 
                     max_pages = 20
                     )
crawler.run()

#view_data("my_database.db")