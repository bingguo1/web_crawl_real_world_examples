from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selectorlib import Extractor
import requests 
import json
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dateutil import parser as dateparser
import csv
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

options = Options()
#options.headless = True
#options.add_argument('--headless')
#options.add_argument('--blink-settings=imagesEnabled=false')
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options, executable_path='/Users/bing/dataScientist/chromedriver')
driver.get("https://www.amazon.com/ECOVACS-N79S-Connectivity-Controls-Self-Charging/product-reviews/B077HW9XM7/ref=cm_cr_getr_d_paging_btm_next_240?ie=UTF8&reviewerType=all_reviews&pageNumber=240")
##driver.get("https://www.amazon.com/ECOVACS-N79S-Connectivity-Controls-Self-Charging/product-reviews/B077HW9XM7/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews")
#driver.get("https://www.amazon.com/iRobot-Roomba-7550-Wi-Fi-Connecte/product-reviews/B07GNPDMRP/ref=cm_cr_getr_d_paging_btm_next_240?ie=UTF8&reviewerType=all_reviews&pageNumber=240")
#driver.get("https://www.amazon.com/Pure-Multi-Floor-Navigation-Selective-Connected/product-reviews/B08BC1RJRV/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews")
#driver.get("https://www.amazon.com/iRobot-Roomba-7550-Wi-Fi-Connecte/product-reviews/B07GNPDMRP/ref=cm_cr_getr_d_paging_btm_next_51?ie=UTF8&reviewerType=all_reviews&pageNumber=51")
#driver.get("https://www.amazon.com/iRobot-Roomba-7550-Wi-Fi-Connecte/product-reviews/B07GNPDMRP/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews")
#driver.get("https://www.amazon.com/iRobot-Roomba-Vacuum-Automatic-Disposal/product-reviews/B08TP1D9X1/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews")
driver.maximize_window()
#time.sleep(3)

e = Extractor.from_yaml_file('amazonReviewCrawl2.yml')
maxNpage=99999
iPage=239

def scrape(raw_html):
    raw_data=e.extract(raw_html)

    if (not raw_data) or len(raw_data) == 0:
        print(" it's empty !!!!!!!!!!!!!!!!!!")
        return False
    
    data = raw_data['review']
    print("--------iPage:------ {}".format(iPage))


    for r in data:
        #        print(r['customerName'])
        date_posted = r['reviewDateLocation'].split('on ')[-1]
        del r['reviewDateLocation']   ### you need to delete this unless you'll put this column into csv fieldnames
        r['date'] = dateparser.parse(date_posted).strftime('%d %b %Y')
        if r['stars']:
            r['stars'] = r['stars'].split(' out of')[0]
        else:
            r['stars'] = r['otherCountryStars'].split(' out of')[0]
        if not r['reviewTitle']:
            r['reviewTitle']=r['otherCountryReviewTitle']        
        if r['nFoundHelpful']:   ### sometimes this is empty
            if "people" in r['nFoundHelpful']:
                r['nFoundHelpful']=r['nFoundHelpful'].split(' people')[0]
            else:
                r['nFoundHelpful']="1"
        else:
            r['nFoundHelpful']="0"
        if 'otherCountryReviewTitle' in r.keys():
            del r['otherCountryReviewTitle']
        if 'otherCountryStars' in r.keys():
            del r['otherCountryStars']
        try:
            writer.writerow(r)
        except:
            print(r)
            exit(0)
    return True

## <a href="/iRobot-Roomba-7550-Wi-Fi-Connecte/product-reviews/B07GNPDMRP/ref=cm_cr_getr_d_paging_btm_5?ie=UTF8&amp;pageNumber=5&amp;reviewerType=all_reviews&amp;pageSize=10">Next page<span class="a-letter-space"></span><span class="a-letter-space"></span>→</a>

lastPage=False
with open('ecovacs_N79S_reviews2.csv','w') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=["customerName","modelName","reviewTitle","date","reviewBody","stars","nFoundHelpful"],quoting=csv.QUOTE_ALL)
    while True:
        if iPage%10==0:
            time.sleep(3)
        print(driver.current_url)
        if iPage>= maxNpage:
            break
        iPage=iPage+1
        ##        nextPageButton=WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.a-last a"))) ### this won't work, cause the old page also contains this
        ##        while True:
        while True:
            time.sleep(0.5)
            try:
                nextPageButton=WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.a-last a")))
                #                nextPageButton=driver.find_element_by_css_selector("li.a-last a")
            except TimeoutException:
                print("reach lastPage !!!!!!!!!!!!!!")
                lastPage=True
                break                
            nextPage=int(nextPageButton.get_attribute('href').split("pageNumber=")[1].split("&reviewerType")[0])
            print("nextPage:{}".format(nextPage))
            if nextPage>iPage:
                break            
        raw_html = driver.page_source
        result=scrape(raw_html)
        #        if not result:
        #            iPage=iPage-1
        if lastPage:
            break;
        nextPageButton.click()

    
#driver.quit()
