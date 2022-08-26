from itertools import product
from wsgiref import headers
import requests
import bs4 as bs
import urllib.request as ur
import csv
import sys

# url = 'https://www.amazon.it/itek-MAJES-Addressable-telecomando-Radiofrequenza/dp/B07L9FMK56'
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}

# page = requests.get(url, headers = headers)

# bs = bs.BeautifulSoup(page.content, 'html.parser')

# findProductTitle = bs.find(id = 'productTitle').get_text()

# productTitle = findProductTitle.strip()

# findPrice = bs.find('span', class_='a-offscreen').get_text()

# prezzo = 'Prezzo --> ' + findPrice + '\n'

def saveInFile(link):
    if link == "":
        return "Link Empty!"
    else:
        localFile = open('file.csv', 'a')
        localFile.writelines(link+'\n')
        localFile.close()
        return 'Link Saved in a CSV File!'

def findProdTitle(link):
    urls = link
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
    page = requests.get(urls, headers = headers)
    bsc = bs.BeautifulSoup(page.content, "lxml")
    findProductTitle = bsc.find(id = 'productTitle').get_text()
    productTitle = findProductTitle.strip()
    return productTitle

def findPrice(link):
    
    urls = link

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
    
    page = requests.get(urls, headers = headers)

    bss = bs.BeautifulSoup(page.content, "lxml")
    
    findPrice = bss.find('span', class_='a-offscreen').get_text()

    prezzo = 'Prezzo --> ' + findPrice + '\n'
    
    return prezzo


