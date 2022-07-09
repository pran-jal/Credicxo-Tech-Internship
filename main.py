import traceback
import requests as r
import csv
from bs4 import BeautifulSoup
import re
import undetected_chromedriver as uc
import random
import time
import json

agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
            # 'Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, Like Gecko) Version/6.0.0.141 Mobile Safari/534.1+',
            # 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
            'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
            'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3',
            # 'Mozilla/5.0 (Linux; U; Android 0.5; en-us) AppleWebKit/522+ (KHTML, like Gecko) Safari/419.3',
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Opera/9.00 (Windows NT 5.1; U; en)',
        ]

headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
}

def a_price(url, asin, headers):        # scrape price
    price = None
    if r.get(url).status_code == 200:
        pass
    else:
        try:
            headers['referer'] = r.head(url).headers['Location']
        except:
            print(r.head(url).headers)
        price_offer_list = r.get(f'https://www.amazon.de/gp/product/ajax/ref=auto_load_aod?asin={asin}&pc=dp&experienceId=aodAjaxMain', headers=headers).content
        soup = BeautifulSoup(price_offer_list, 'html.parser')
        prices = soup.find_all("span",{"class":"a-offscreen"})
        price = [re.sub(re.compile("[ ]*\\u[a-z0-9]{4}[ ]*"), '\n', i.text.strip().strip('\u20ac')) for i in prices]
        print(price)
    return price

def scrape(page, url, headers):     # scrape all and calls price scraper
    soup = BeautifulSoup(page, 'html.parser')
    
    product_title = soup.find("span", {'id': "productTitle"}).text.strip()

    space = re.compile("[ \n\t]{2,}")
    try:
        details = re.sub(space, '\n', soup.find("table", {"id": "productDetails_techSpec_section_1"}).text)
    except:
        details = re.sub(space, '\n', soup.find("div", {"id":"detailBullets_feature_div"}).text)
    
    details = details.split('\n')
    for i in details:
        details[details.index(i)] = i.strip().strip('\u200e')
    i = 0
    len_D = len(details)
    detail = {}
    while i<len_D:
        while True and i<len_D:
            if details[i] == '' or details[i] == ':':
                del details[i]
                len_D -= 1
            else:
                break
        else:break
        while True and i<len_D-1:
            if details[i+1] == '' or details[i+1] == ':':
                del details[i+1]
                len_D -= 1
            else:
                break
        else:break
        detail[details[i]] = details[i+1]
        i=i+2
    
    price = None
    price_s = soup.find("div", {"id":"tmmSwatches"})
    if price_s is not None:
        price = price_s.text
    else:
        link_of_p = soup.find("span",{"data-action":"show-all-offers-display"}).find("a", {"class": "a-button-text"})
        if link_of_p is not None:
            url = url.split('/dp/')
            link = url[0]+link_of_p['href']
            price = a_price(link, url[1], headers)
        else:
            price_list = soup.find_all("span", {"class":"a-offscreen"})
            price = [re.sub(re.compile("[A-Za-z \n\t,\\]*"), '\n', i.text.strip().strip('\u20ac')) for i in price_list]

    try:
        image = soup.find("img", {"id": "landingImage"})['src']
    except:
        image = soup.find("img", {"id": "imgBlkFront"})['src']
    
    return {
        "title":product_title,
        "image_url": image,
        "price": price,
        "details": detail
    }

def sel(url, headers):              # selenium in case scraper detected
    browser = uc.Chrome()
    browser.get(url)
    source = browser.page_source
    time.sleep(1)
    browser.quit()
    return scrape(source, url, headers)

def main():
    f = open("Amazon Scraping - sheet1.csv", 'r')
    csv_file = csv.reader(f)

    to_json = []
    count = 0

    begin = time.time()

    for line in csv_file:
        
        count +=1
        print(count)
        
        asin = line[2]
        country = line[3]
        headers['referer'] = f"https://www.amazon.{country}"
        headers['user-agent'] = random.choice(agents)
        
        url = f"https://www.amazon.{country}/dp/{asin}"
        a = r.get(url, headers=headers)
    
        if a.status_code == 200:
            try:
                to_json.append(scrape(a.content, url, headers))
            except:
                error = traceback.print_exc()
                try:
                    to_json.append(sel(url, headers))
                except:
                    to_json.append({"Error": f"the {url} not available"})
        else:
            to_json.append({"Error": f"the {url} not available"})
        
        if count == 100:
            end = time.time()
            print(line[0], " done -", "%.2f" %end - begin, "seconds")
            begin = time.time()
            count = 0
            j = open('scraped.json', 'a', encoding='utf-8')
            json.dump(to_json, j)
            j.close()

    end = time.time()
    print(line[0], " done -", ":.2f".format(end - begin), "seconds")
    count = 0
    j = open('scraped.json', 'a', encoding='utf-8')
    json.dump(to_json, j)
    j.close()

if __name__ == '__main__':
    main()




