import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidArgumentException, WebDriverException
from bs4 import BeautifulSoup

class Scraper:
    """Base scraper class for web scraping tasks using Selenium."""

    def __init__(self):
        """Initializes the scraper with basic configurations."""
        self.initialize()
    
    def initialize(self):
        """Resets the internal state of the scraper."""
        self.results = []
        self.html = []
        self.merged = []

    def open_webdriver(self):
        """Opens a Chrome WebDriver session with specific options."""
        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'none'
        options.add_argument("--window-size=320,240")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-infobars')
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument('--mute-audio')
        options.add_argument('incognito')
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 1
        })

        self.webdriver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.webdriver, 30)

    def close_webdriver(self):
        """Closes the WebDriver session."""
        if self.webdriver:
            self.webdriver.quit()

    def get_html(self, url: str) -> str:
        """
        Retrieves the HTML content of the specified URL.

        Args:
            url (str): The URL to retrieve the HTML from.

        Returns:
            str: The HTML content of the page.
        """
        try:
            self.webdriver.get(url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            html = self.webdriver.page_source
            self.webdriver.execute_script("window.stop();")
            return html

        except (InvalidArgumentException, WebDriverException) as e:
            print(f"Exception occurred: {e}")
            return ""

    def append_info(self, html: str):
        """
        Appends the extracted information from the HTML content.

        Args:
            html (str): The HTML content to extract information from.
        """
        self.html.append(html)
        res = self.get_info(html)
        self.results.append(res)

    def get_pages(self, query: str, page_num: int = 100):
        """Placeholder method to be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement this method.")

    def extract_tags(self, html: str):
        """Placeholder method to be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement this method.")

    def get_info(self, html: str):
        """Placeholder method to be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement this method.")

    def make_dataframe(self):
        """Converts the scraped results into a pandas DataFrame."""
        self.merged = [item for pages in self.results for item in pages]
        self.df = pd.DataFrame(self.merged)

    def save_csv(self, file_path: str = "./results.csv"):
        """Saves the DataFrame to a CSV file."""
        if hasattr(self, 'df'):
            self.df.to_csv(file_path, index=False)
        else:
            print("No data available to save. Please run the scraper first.")

class GoogleScraper(Scraper):
    """Scraper class specifically for extracting information from Google search results."""

    def get_pages(self, query: str, page_num: int = 100):
        """
        Retrieves multiple pages of Google search results.

        Args:
            query (str): The search query URL.
            page_num (int, optional): The number of pages to scrape. Defaults to 100.
        """
        self.webdriver.get(query)
        process = True
        next_page = False

        while process and len(self.html) < page_num:
            if next_page:
                next_btn = self.webdriver.find_element(By.XPATH, '//*[@id="pnnext"]')
                next_btn.click()

            try:
                self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="pnnext"]')))
                next_page = True
            except:
                process = False
            finally:
                html = self.webdriver.page_source
                self.append_info(html)

    def extract_tags(self, elements):
        """
        Extracts relevant tags from search result elements.

        Args:
            elements (list): List of anchor tag elements from the search results.

        Returns:
            list: A list of dictionaries containing extracted information.
        """
        extracted = []

        for element in elements:
            info = {}
            link = element.get('href')

            if len(link) > 5:
                info['link'] = link

                h3 = element.find('h3')
                if h3:
                    info['title'] = h3.text

                span = element.find_all('span')
                for item_span, item_name in zip(span, ['', 'author', 'category']):
                    if item_span.text:
                        info[item_name] = item_span.text

                extracted.append(info)
        return extracted

    def get_info(self, html: str):
        """
        Extracts information from the HTML content of a Google search result page.

        Args:
            html (str): The HTML content of the page.

        Returns:
            list: A list of dictionaries containing the extracted information.
        """
        soup = BeautifulSoup(html, 'html.parser')
        search_results = soup.find(attrs={'id': 'search'})
        anchor_tags = search_results.find_all('a')

        extracted_info = self.extract_tags(anchor_tags)
        descriptions = search_results.find_all('div', {'style': "-webkit-line-clamp:2"})

        for description, info in zip(descriptions, extracted_info):
            info['desc'] = description.text

        return extracted_info
