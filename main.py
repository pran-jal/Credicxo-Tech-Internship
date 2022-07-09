import requests as r
import csv
from bs4 import BeautifulSoup
# from selenium import webdriver
import random
import time
import json
agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
            'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
        ]

headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': random.choice(agents),
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
}

def scrape(page, url):
    soup = BeautifulSoup(page, 'html.parser')
    
    product_title = soup.find("span", {'id': "productTitle"}).text.strip()
    
    try:
        details = soup.find("table", {"id": "productDetails_techSpec_section_1"}).text.strip()
    except:
        details = soup.find("div", {"id":"detailBullets_feature_div"}).text
    
    price_list = soup.find_all("span", {"class":"a-offscreen"})
    price_list = [i.text for i in price_list]
    price = soup.find_all("span", {"class":"a-color-base"})
    price_list.extend([i.text for i in price])
    # price_list2 = soup.find_all("span", {"class":"a-price"})
    # price_list.extend([i.text for i in price_list2])
    
    try:
        image = soup.find("img", {"id": "landingImage"})['src']
    except:
        image = soup.find("img", {"id": "imgBlkFront"})['src']
    
    price = ["a-offscreen", 'a-price-whole', 'priceblock_ourprice', 'aod-container', 'a-section a-spacing-small a-spacing-top-small',
    ]

    # print(product_title, image, details, price_list)
    return {
        "title":product_title,
        "image_url": image,
        "price": price_list,
        "details": details
    }


f = open("Amazon Scraping - sheet1.csv", 'r')
csv = csv.reader(f)

to_json = []
count = 0
begin = time.time()
for line in csv:
    count +=1
    asin = line[2]
    country = line[3]
    headers['referer'] = f"https://www.amazon.{country}"
    url = f"https://www.amazon.{country}/dp/{asin}"
    print(count)
    a = r.get(url, headers=headers)
    if a.status_code == 200:
        to_json.append(scrape(a.content, headers['referer']))
    else:
        to_json.append({"Error": f"the {url} not available"})
    # print(to_json)
    # f = open('scraped.json', 'a', encoding='utf-8')
    if count == 100:
        end = time.time()
        print(end - begin)
        begin = time.time()
        count = 0
        f = open('scraped.json', 'a', encoding='utf-8')
        json.dump(to_json, f)
        
print('end')






