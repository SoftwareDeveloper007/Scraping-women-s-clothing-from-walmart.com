from urllib import *
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen
import urllib.request
import requests
from io import BytesIO

from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from dateutil.relativedelta import *

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
        pass



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
    html = download("https://www.walmart.com/cp/womens-clothing-apparel/133162")
    print(html)
