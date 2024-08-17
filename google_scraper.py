import pandas as pd

from bs4 import BeautifulSoup

# from webscraping import ArticleScraper

from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidArgumentException, WebDriverException
# from selenium.webdriver.common.action_chains import ActionChains 
# from selenium.webdriver.common.keys import Keys

class Scraper:

    def __init__(self):
        self.initialize()
        # self.open_webdriver()

    def initialize(self):
        self.results = []
        self.html = []
        self.merged = []


    def open_webdriver(self):
        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'none'
        # options.add_argument('headless')
        # options.add_argument('window-size=640x480')
        # options.add_argument("disable-gpu")
        options.add_argument("--window-size=320,240")
        # options.add_argument('--headless')
        # options.add_argument('--log-level=3')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-infobars')
        options.add_argument('--blink-settings=imagesEnabled=false') #브라우저에서 이미지 로딩을 하지 않습니다.
        options.add_argument('--mute-audio') #브라우저에 음소거 옵션을 적용합니다.
        options.add_argument('incognito') #시크릿 모드의 브라우저가 실행됩니다.
        # 알림창 끄기
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 1
        })
        self.webdriver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.webdriver, 30)


    def close_webdriver(self):
        self.webdriver.close()
        self.webdriver.quit()

    def get_html(
        self,
        url: str
    ) -> str:
        try:
            self.webdriver.get(url)
            element = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            html = self.webdriver.page_source
            self.webdriver.execute_script("window.stop();")
            return html
        
        except InvalidArgumentException as e:
            print(f"Invalid argument exception: {e}")
            return ""
    
        except WebDriverException as e:
            print(f"WebDriverException: {e}")
            return ""
    
        finally:
            pass


    def append_info(self):
        html = self.webdriver.page_source
        self.html.append(html)
        res = get_info(html)
        self.results.append(res)
    

    def get_pages(self, query, page_num=100):
        pass


    def extract_tags(self):
        pass

    
    def get_info(self):
        pass


    def make_dataframe(self):
        for pages in self.results:
            for item in pages:
                self.merged.append(item)
        self.df = pd.DataFrame(self.merged)

    def save_csv(self, file_path="./results.csv"):
        self.df.to_csv(file_path, index=False)



class GoogleScraper(Scraper):
    
    def get_pages(self, query, page_num=100):
        self.webdriver.get(query)
        process = True
        next_page = False
        while process:
            if next_page:
                elem = self.webdriver.find_element(By.XPATH, '//*[@id="pnnext"]')
                elem.click()
            else:
                next_page = True

            try:
                wait = WebDriverWait(self.webdriver, 5)
                # wait.until(EC.staleness_of(elem))
                wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="pnnext"]')))
            except:
                process = False
            finally:
                html = self.webdriver.page_source
                self.html.append(html)
                res = self.get_info(html)
                self.results.append(res)
        # self.close_webdriver()


    def extract_tags(self, a):
        exts = []
    
        for item in a:
            info = {}
        
            link = item['href']
            if len(link) > 5:
                # print(link)
                info['link'] = link
                
                h3 = item.find('h3')
                if h3 != None:
                    # print(h3.text)
                    info['title'] = h3.text
                else:
                    continue
            
                span = item.find_all('span')
                for item_span, item_name in zip(span, ['', 'author', 'category']):
                # for item_span in span:
                    if len(item_span.text) > 0:
                        # print(item_span.text)
                        info[item_name] = item_span.text
            
                # print()
                exts.append(info)
        return exts
    
    
    def get_info(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        id_search = soup.find(attrs={'id':'search'})
        a = id_search.find_all('a')
        exts = self.extract_tags(a)
        desc = id_search.find_all('div', {'style':"-webkit-line-clamp:2"})
        for item, ext in zip(desc, exts):
            ext['desc'] = item.text
            # print(item.text)
        return exts