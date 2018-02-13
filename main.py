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
import time, re, collections, shutil, os, sys, zipfile, xlrd, threading


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

    def startScraping(self):
        # html = download(self.base_url)
        # print(html)
        # soup = BeautifulSoup(html, "html.parser")
        #
        # rows = soup.select("ul.slider-list")
        # sub_urls_1 = []
        #
        # for i, row in enumerate(rows):
        #     if i in [1, 2]:
        #         cols = row.select("div.TempoCategoryTile-tile")
        #         for j, col in enumerate(cols):
        #             # print(col.get('href'))
        #             print(col.text)
        #             # sub_urls_1.append()

        # driver = webdriver.PhantomJS('WebDriver/phantomjs.exe')
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--disable-gpu')  # Last I checked this was necessary.
        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='WebDriver/chromedriver.exe')
        driver.maximize_window()
        driver.get(self.base_url)

        print(driver.page_source)

        links = driver.find_elements_by_css_selector("a.TempoCategoryTile-tile-overlay")
        print(len(links))




def download(url, num_retries=3):
    """Download function that also retries 5XX errors"""
    try:
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


        headers = {'User-agent': 'your bot 0.1'}
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
    app = mainScraper()
    app.startScraping()