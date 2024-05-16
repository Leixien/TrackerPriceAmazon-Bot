import requests
from bs4 import BeautifulSoup
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
    
    try:
        page = requests.get(urls, headers = headers)
        page.raise_for_status()
    except requests.RequestException as e:
        print(f"Errore nella richiesta: {e}")
        return None
    
    soup = BeautifulSoup(page.content, "lxml")
    product_title_element = soup.find(id='productTitle')

    if product_title_element is not None:
        product_title = product_title_element.get_text().strip()
        return product_title
    else:
        print("Elemento con ID 'productTitle' non trovato")
        return None

def findPrice(link):
    
    urls = link

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
    
    page = requests.get(urls, headers = headers)

    bss = BeautifulSoup(page.content, "lxml")
    
    findPrice = bss.find('span', class_='a-offscreen').get_text()

    prezzo = 'Prezzo --> ' + findPrice + '\n'
    
    return prezzo