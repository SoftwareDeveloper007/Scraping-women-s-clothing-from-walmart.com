from urllib import *
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen
import urllib.request
import requests
from io import BytesIO

from urllib.parse import urljoin

from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from dateutil.relativedelta import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time, re, collections, shutil, os, sys, zipfile, xlrd, threading, csv, openpyxl

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-gpu')  # Last I checked this was necessary.
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='WebDriver/chromedriver.exe')
driver.maximize_window()

class log_printer():
    def __init__(self):
        curDate = datetime.now()
        curDateStr = "{:4d}_{:02d}_{:02d}_{:02d}_{:02d}_{:02d}".format(curDate.year, curDate.month, curDate.day,
                                                                       curDate.hour, curDate.minute, curDate.second)
        self.logFile = open("Log_File_" + curDateStr + ".txt", "w+")

    def print_log(self, logTxt):
        try:
            self.logFile.write(logTxt + '\n')
            self.logFile.flush()
        except:
            pass
        print(logTxt + '\n')

    def close_log(self):
        self.logFile.close()

class mainScraper():
    def __init__(self):
        self.base_url = "https://www.walmart.com/cp/womens-clothing-apparel/133162"
        self.total_data = []
        self.log_printer = log_printer()

        self.dest = "Result"
        self.outfile_name = "total.xlsx"

        if not os.path.exists(self.dest):
            os.makedirs(self.dest)

    def totalScraping(self):
        self.input_data = []
        temp_data = []

        input_xlsx = xlrd.open_workbook("links.xlsx")
        sheet = input_xlsx.sheet_by_index(0)
        for i in range(sheet.nrows):
            row = [sheet.row(i)[j].value for j in range(len(sheet.row(i)))]
            if row[1] not in temp_data:
                self.input_data.append([i] + row)
                temp_data.append(row[1])

        self.wb = openpyxl.Workbook()
        self.ws = self.wb.active


        self.threads = []
        self.max_threads = 10

        for i in range(self.max_threads):
            self.drivers.append(None)

        logTxt = "------------------------ Scraping started on! ------------------------"
        self.log_printer.print_log(logTxt)

        while self.threads or self.input_data:
            for thread in self.threads:
                if not thread.is_alive():
                    self.threads.remove(thread)

            while len(self.threads) < self.max_threads and self.input_data:
                thread = threading.Thread(target=self.scrapingByURL)
                thread.setDaemon(True)
                thread.start()
                self.threads.append(thread)

        for driver in self.drivers:
            try:
                driver.quit()
            except:
                pass
        self.drivers.clear()

    def scrapingByURL(self):

        index, type, url = self.input_data.pop()
        driver = self.drivers.pop()
        # index, key, url = (1, "Swimwear", "https://www.walmart.com/ip/Senfloco-Sexy-Bodycon-Off-the-Shoulder-Dacron-One-piece-Swimsuit-for-Women-Flouncing-Overlay-Top/861915977")
        # driver = None

        if driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument('--disable-gpu')  # Last I checked this was necessary.
            driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='WebDriver/chromedriver.exe')
            driver.maximize_window()

        driver.get(url)

        try:
            id = driver.find_element_by_css_selector("div.wm-item-number").text.strip()
        except:
            id = ""
        try:
            title = driver.find_element_by_css_selector("div.ProductTitle").text.strip()
        except:
            title = ""
        try:
            desc = driver.find_element_by_css_selector("div.about-desc").text
        except:
            desc = ""
        try:
            try:
                sale_price = driver.find_element_by_css_selector("div.prod-ProductOffer > div > div > span").text
                try:
                    sub_prices = []
                    sub_price_cols = driver.find_elements_by_css_selector("div.prod-ProductOffer > div > div > div > div > div")
                    for sub_price_col in sub_price_cols:
                        sub_prices.append(sub_price_col.text)
                    sub_price = " | ".join(sub_prices)

                except:
                    sub_price = ""

                all_price = " | ".join([sale_price, sub_price])

            except:
                all_price = ""
                sale_price = ""

        except:
            all_price = ""
            sale_price = ""

        color = ""
        try:
            variant_boxes = driver.find_elements_by_css_selector("div.prod-VariantWrapper")
            colors = []
            for i, variant_box in enumerate(variant_boxes):
                label = variant_box.find_element_by_css_selector("div.prod-ProductVariantType-label").text
                if "Color" in label:
                    color_panels = variant_box.find_elements_by_css_selector("div.prod-VariantGridItem")
                    for color_panel in color_panels:

                        colors.append(color_panel.get_attribute('textContent'))
                    color = " | ".join(colors)
                    break

        except:
            color = ""

        try:
            image_box = driver.find_element_by_css_selector("div.prod-HeroImage > div > img")
            image_url = image_box.get_attribute("src")

            r2 = requests.get(image_url)

            if not os.path.exists(self.dest + "/" + type):
                os.makedirs(self.dest + "/" + type)

            image_name = "Result/" + type + "/" + title + ".jpg"
            with open(image_name, "wb") as f:
                f.write(r2.content)

        except:
            pass

        logTxt = "+-+-+-+-+-+-+-+-+-+-+-+-+- {0}, {1}, {2} +-+-+-+-+-+-+-+-+-+-+-+-+-\n".format(index, type, title)
        self.log_printer.print_log(logTxt)

        logTxt = "\turl:\t{}\n".format(url)
        self.log_printer.print_log(logTxt)

        logTxt = "\tid:\t{}\n".format(id)
        self.log_printer.print_log(logTxt)

        logTxt = "\ttype:\t{}\n".format(type)
        self.log_printer.print_log(logTxt)

        logTxt = "\ttitle:\t{}\n".format(title)
        self.log_printer.print_log(logTxt)

        logTxt = "\tdesc:\t{}\n".format(desc)
        self.log_printer.print_log(logTxt)

        logTxt = "\tcolor:\t{}\n".format(color)
        self.log_printer.print_log(logTxt)

        logTxt = "\tall_price:\t{}\n".format(all_price)
        self.log_printer.print_log(logTxt)

        logTxt = "\tsale_price:\t{}\n".format(sale_price)
        self.log_printer.print_log(logTxt)

        self.ws.cell(row=index+1, column=1).value = url
        self.ws.cell(row=index+1, column=2).value = id
        self.ws.cell(row=index+1, column=3).value = type
        self.ws.cell(row=index+1, column=4).value = title
        self.ws.cell(row=index+1, column=5).value = desc
        self.ws.cell(row=index+1, column=6).value = color
        self.ws.cell(row=index+1, column=7).value = all_price
        self.ws.cell(row=index+1, column=8).value = sale_price
        self.wb.save(self.dest + "/" + self.outfile_name)

        self.drivers.append(driver)

    def get_sub_urls_1(self):
        html = download(self.base_url)
        soup = BeautifulSoup(html, "html.parser")

        lis = soup.select("li.SideBarMenuModuleItem")
        self.sub_urls_1 = {}

        filename = "links.xlsx"
        dest = "E://tmp/2018.02.13 Looking for a web scraper to extract list of items from e commerce site/"
        wb = openpyxl.Workbook()
        ws = wb.active
        total_cnt = 0

        for i, li in enumerate(lis):
            name = li.text.strip()
            link = li.select_one("a").get("href")

            links = get_sub_urls_2(link)

            for link in links:
                total_cnt += 1
                link = urljoin(self.base_url, link)
                ws.cell(row=total_cnt, column=1).value = name
                ws.cell(row=total_cnt, column=2).value = link
                wb.save(dest + filename)



        # for i, (key, value) in enumerate(self.sub_urls_1.items()):
        #     for j, link in enumerate(value):
        #         ws.cell(row=i+1, column=1).value = key
        #         ws.cell(row=i+1, column=2).value = link
        #         wb.save(filename)

def get_sub_urls_2(url):
    url = urljoin("https://www.walmart.com/cp/womens-clothing-apparel/133162", url)
    page_urls = []
    sub_urls = []
    for i in range(1, 26):
        page_urls.append(url + "?page={}#searchProductResult".format(i))

    for i, new_url in enumerate(page_urls):
        print(i, new_url)
        try:
            global driver
            driver.get(new_url)
            time.sleep(2)
            # print(driver.page_source)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            links = driver.find_elements_by_css_selector("a.product-title-link")
            print(len(links))
            if len(links) == 0:
                break

            # html = download(new_url)
            # # print(html)
            # soup = BeautifulSoup(html, "html.parser")
            # links = soup.select("a.product-title-link")
            for link in links:
                # sub_urls.append(link.get("href"))
                sub_urls.append(link.get_attribute("href"))
                print(link.get_attribute("href"))
        except:
            global options
            driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='WebDriver/chromedriver.exe')
            driver.maximize_window()
            break

    return sub_urls



def download(url, num_retries=3):
    """Download function that also retries 5XX errors"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


        # headers = {'User-agent': 'Ruel.ME Walmart Scraper'}
        result = requests.get(url, headers=headers, stream=True)
        html = result.content.decode()

    except urllib.error.URLError as e:
        print('Download error:', e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry 5XX HTTP errors
                html = download(url, num_retries - 1)
    except:
        html = None
    return html

if __name__ == '__main__':
    start_time = time.time()
    # scrapingURL("https://www.walmart.com/ip/Nlife-Women-Halter-Neck-Open-Back-One-Piece-Pure-Color-Monokinis-Swimwear/881869640", "Swimwear")
    # scrapingURL("https://www.walmart.com/ip/Senfloco-Sexy-Bodycon-Off-the-Shoulder-Dacron-One-piece-Swimsuit-for-Women-Flouncing-Overlay-Top/861915977", "Swimwear")
    app = mainScraper()
    app.totalScraping()

    print(time.time() - start_time)

