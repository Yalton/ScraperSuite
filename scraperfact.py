from bs4 import BeautifulSoup 
import requests 

class ScaperSystem(ABC):
    
    def __init__(self, url, tags, classes, system_id, system_label):
        # Connect to api
        # Connect to BrokenPipeError
        # Save fields to class
        self.api = api
        self.symbol = symbol
        self.time_frame = time_frame
        self.system_id = system_id
        self.system_label = system_label

    @abstractmethod
    def scrape_website(self):
        pass

    @abstractmethod
    def place_sell_order(self):
        pass

    @abstractmethod
    def system_loop(self):
        pass