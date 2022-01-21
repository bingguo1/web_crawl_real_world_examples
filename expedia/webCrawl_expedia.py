import traceback
from playsound import playsound
import sys
import csv
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options

import time

oldtime=datetime.datetime.now()
newtime=None

timelist=[0,0,0]
options = Options()
#options.headless = True
#options.add_argument('--headless')
#options.add_argument('--blink-settings=imagesEnabled=false')
options.add_argument("--start-maximized")
driver=None
##options.add_argument("--window-size=1920,1080")
##options.add_argument("--disable-gpu")
##//*[@id="uitk-tabs-button-container"]/div/li[2]/a/span
##/html/body/div[1]/div[1]/div/div[1]/div/div[1]/div[4]/div/div/div/div[2]/div/div/div/div[2]/div/form/div[2]/ul/div/li[2]/a/span
flyFrom=sys.argv[1] ##"DTW"
flyTo=sys.argv[2]
print(" flyFrom:{},  flyTo:{}".format(flyFrom, flyTo))
#dateSearch = datetime.datetime(2021, 10, 2)
dateSearch=datetime.datetime(int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]) )
#nDays2Search=int(sys.argv[4])
dateEnd=datetime.datetime(int(sys.argv[6]),int(sys.argv[7]),int(sys.argv[8]) )
print("----date start:{}".format(dateSearch))
#dateEnd=dateSearch + datetime.timedelta(days=(nDays2Search-1))
print("-----> ---> dateEnd:  {}".format(dateEnd))

#date += timedelta(days=1)
outfile=open('flights_expedia_{}_to_{}_{}_{}_{}_to_{}_{}_{}.csv'.format(flyFrom, flyTo, dateSearch.month, dateSearch.day, dateSearch.year,dateEnd.month, dateEnd.day, dateEnd.year ), mode='w')
out_writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)




### two problems when clicking the search:
#### web problem 1: 
# Sorry, we couldn't find any flights from Detroit (DTW) to Shanghai (PVG) on Tue, Sep 14  ---> h3 class="uitk-heading-5"
# These airports may not have regularly scheduled flights or there may be restrictions that impact this route.
# Search different dates
# Search different dates
# Departing on Mon, Sep 13,1 day earlier from Tue, Sep 14
### normally there are 3 dates to choose, the first one is older date, the next twos are newer dates --> button class="uitk-card-link"


### web problem 2: (sep 11)
# Sorry, we're having a problem on our end.
# Please try your search again later.
## h2 class="uitk-heading-5 uitk-spacing uitk-spacing-margin-blockend-two"
### select date : button data-stid="open-date-picker"



def chooseAdate(date, checkAvailable=False):  #### MM/DD/YYYY 
    ### September 2021 -> class="uitk-date-picker-month-name uitk-type-medium"
    ### click left/right to select prev/next month: button : data-stid="date-picker-paging"

    monthWant=date.month
    dateWant=date.day
    yearWant=date.year

        
    #        print("monthWant: {0}, dateWant{1}, yearWant{2}".format(monthWant,dateWant,yearWant))
    
    #        monthYear=driver.find_element_by_css_selector(".uitk-date-picker-month-name").text.split()
    # time.sleep(0.5)
    
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-day='1']")))
    
    monthYear=driver.find_element_by_css_selector( ".uitk-date-picker-month-name").text.split()
    #        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".uitk-date-picker-month-name"))).text.split()
    monthName=monthYear[0]
    datetime_object = datetime.datetime.strptime(monthName, "%B")
    month = datetime_object.month
    year=int(monthYear[1])
    
    nClickNext= monthWant+yearWant*12-(month+year*12)
    if nClickNext>0 :
        for i in range(nClickNext):
            driver.find_elements_by_css_selector("button[data-stid='date-picker-paging']")[1].click()

    if nClickNext<0:
        for i in range(abs(nClickNext)):
            driver.find_elements_by_css_selector("button[data-stid='date-picker-paging']")[0].click()
    dateButton=WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-day='{}']".format(dateWant))))
    if checkAvailable:
        if dateButton.get_attribute("data-day-content")=="-":
            return False

    dateButton.click()
    return True




def writeToFile(prices,departureTimes,journeyDurations, layovers, flightOperateds):
    global newtime
    global oldtime
    global dateSearch
    ## '$999
    ## '2:30pm - 6:40am'
    ## '27h 10m (2 stops)'
    ## ['Air Canada • Air Canada 8818 operated by Air Canada Express - Jazz', 'Air Canada • Air Canada 8816 operated by Air Canada Express - Jazz', 'Air Canada • Air Canada 8814 operated by Air Canada Express - Jazz', 'Multiple airlines']

    if dateSearch>dateEnd:
        print(" !!!!!! eixt() due to dateSearch>dateEnd)")
        return
    nRow=len(flightOperateds)

    newtime=datetime.datetime.now()
    tdiff=(newtime-oldtime).seconds
    timelist.pop(0)
    timelist.append(tdiff)
    
    print(" *********** filling date :{}, with seconds:{}".format(dateSearch, tdiff))
    oldtime=newtime
    for i in range(nRow):
        if "Nonstop" in journeyDurations[i]:
            layovers.insert(i,"none")
    for i in range(nRow):
        out_writer.writerow([ flyFrom, flyTo, dateSearch.strftime("%x"),  prices[i], departureTimes[i], journeyDurations[i], layovers[i], flightOperateds[i] ])        

    # if (timelist[0]+timelist[1]+timelist[2])>29:
    #     dateSearch+=datetime.timedelta(days=1)
    #     print("----> ----------> ---------> !!!!!!!!!!! too long, will redo ------------ ")
    #     driver.quit()
    #     time.sleep(2)
    #     main()
    
        
def solve_couldnot_find():
    global dateSearch
    print("------------------ solve_couldnot_find -------------------------")
    iButton=0
    #### the one to choose is not always the second one
    for i in range(3):
        ### show date:  Thu, Sep 16,   --> h3 class="uitk-type-left uitk-heading-6"
        dateString=driver.find_elements_by_css_selector("h3[class='uitk-type-left uitk-heading-6']")[i].text.split(",")[1]
        date=datetime.datetime.strptime(dateString+" "+str(dateSearch.year), " %b %d %Y")
        if dateSearch<date:
            dateSearch=date
            iButton=i
            break

    print(" --------------> -------> -> new date within solve_couldnot_find: {} ".format(dateSearch))

    driver.find_elements_by_css_selector("button.uitk-card-link")[iButton].click()

    

def solve_problem_our_end():
    print("----------------------------------  solv_problem_our_end -------------------------------------------")
    ### select date : button data-stid="open-date-picker"
    driver.find_element_by_css_selector("button[data-stid='open-date-picker']").click()
    global dateSearch
    while True:
        dateSearch+=datetime.timedelta(days=1)
        print("start to choose a date")
        if chooseAdate(dateSearch, True):
            break;
    print(" --------------> -------> -> new date within solve_problem_our_end :{}".format(dateSearch))

    driver.find_element_by_css_selector("button[data-stid='apply-date-picker']").click()
    driver.find_element_by_name("searchButton").click()



def getData():
    ### span.uitk-lockup-price
    ## WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.uitk-lockup-price")))
    while True:
        # try:
        #     t0=datetime.datetime.now()
        #     # div data-test-id="intersection-observer"
        #     #            nList=len(WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a[data-test-id='goto-opinion-lab-button']"))))
        #     nList=len(WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div[data-test-id='intersection-observer']"))))
        #     tdiff=(datetime.datetime.now()-t0).seconds
        #     if tdiff>3:
        #         print("locate intersection-observer  with {} seconds".format(tdiff))
        # except:
        #     print("^^^^^ sleep 3 seconds")
        #     time.sleep(3)

        #     #           nList=len(WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a[data-test-id='goto-opinion-lab-button']"))))
        #     try:
        #         nList=len(WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div[data-test-id='intersection-observer']"))))
        #     except Exception as e:
        #         print("print error---")
        #         print(e)
        #         recover()

        # lists=driver.find_elements_by_css_selector("li[data-test-id='offer-listing']")
        #    print("how many offers: {}, nlist: {}".format(len(lists), nList))
        # lists=WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "li[data-test-id='offer-listing']")))
        ### div : data-test-id="failed-request-messaging"
        time.sleep(0.5)
        if len(driver.find_elements_by_css_selector("li[data-test-id='offer-listing']"))>0:
            break
        else:    
            try:
                #                driver.find_element_by_css_selector("div[data-test-id='alternate-dates-container']")
                print(driver.find_element_by_xpath("//*[@id='app-layer-base']/div[2]/div[3]/div/section/main/div[2]/div/div[1]/h3").text)
                solve_couldnot_find()
            except NoSuchElementException:
                try:
                    driver.find_element_by_css_selector("div[data-test-id='failed-request-messaging']")
                    print("start solve_problem_our_end ")
                    solve_problem_our_end()
                    print("finished solve_problem_our_end ")
                except:
                    pass
        

    t0=datetime.datetime.now()
    
    WebDriverWait(driver, 8).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div[data-test-id='journey-duration']")))

        
    tdiff=(datetime.datetime.now()-t0).seconds
    if tdiff>3:
        print("locate  div[data-test-id='journey-duration']  with {} seconds".format(tdiff))
    try:
        priceEles= driver.find_elements_by_css_selector("span.uitk-lockup-price")
        prices=[ ele.text  for ele in priceEles]
    except StaleElementReferenceException:
        time.sleep(0.5)
        priceEles= driver.find_elements_by_css_selector("span.uitk-lockup-price")
        prices=[ ele.text  for ele in priceEles]
 
    
    ##        data-test-id="departure-time"
    try:
        departureTimeEles=driver.find_elements_by_css_selector("span[data-test-id='departure-time']")
        departureTimes=[ ele.text for ele in departureTimeEles]
    except StaleElementReferenceException:
        time.sleep(0.5)
        departureTimeEles=driver.find_elements_by_css_selector("span[data-test-id='departure-time']")
        departureTimes=[ ele.text for ele in departureTimeEles]
 
    
    ##        data-test-id="journey-duration"
    try:
        journeyDurationEles=driver.find_elements_by_css_selector("div[data-test-id='journey-duration']")
        journeyDurations=[ ele.text for ele in journeyDurationEles]
    except StaleElementReferenceException:
        time.sleep(0.5)
        journeyDurationEles=driver.find_elements_by_css_selector("div[data-test-id='journey-duration']")
        journeyDurations=[ ele.text for ele in journeyDurationEles]

    #### data-test-id="layovers"
    try:
        layoversEles=driver.find_elements_by_css_selector("div[data-test-id='layovers']")
        layovers=[ ele.text for ele in layoversEles]
    except StaleElementReferenceException:
        time.sleep(0.5)
        layoversEles=driver.find_elements_by_css_selector("div[data-test-id='layovers']")
        layovers=[ ele.text for ele in layoversEles]
        
    
    ##        data-test-id="flight-operated"
    try:
        flightOperatedEles=driver.find_elements_by_css_selector("div[data-test-id='flight-operated']")
        flightOperateds= [ ele.text for ele in flightOperatedEles]
    except StaleElementReferenceException:
        time.sleep(0.5)
        flightOperatedEles=driver.find_elements_by_css_selector("div[data-test-id='flight-operated']")
        flightOperateds= [ ele.text for ele in flightOperatedEles]
 

    if len(prices)> len(flightOperateds):
        prices.pop(0)
    else:
        if len(flightOperateds)>  len(prices):
            priceEles= driver.find_elements_by_css_selector("span.uitk-lockup-price")
            prices=[ ele.text  for ele in priceEles]
            #            print("------new prices-----")
        if len(flightOperateds)> len(departureTimes):
            departureTimeEles=driver.find_elements_by_css_selector("span[data-test-id='departure-time']")
            departureTimes=[ ele.text for ele in departureTimeEles]
            #            print("------new departureTimes-----")
        if len(flightOperateds) >len(journeyDurations):
            journeyDurationEles=driver.find_elements_by_css_selector("div[data-test-id='journey-duration']")
            journeyDurations=[ ele.text for ele in journeyDurationEles]
            #            print("------new journeyDurations-----")
        if len(flightOperateds)>len(layovers):
            layoversEles=driver.find_elements_by_css_selector("div[data-test-id='layovers']")
            layovers=[ ele.text for ele in layoversEles]
            #            print("------new layovers-----")

    # print(prices)
    # print(departureTimes)
    # print(journeyDurations)
    # print(layovers)
    # print(flightOperateds)
            
    
    writeToFile(prices,departureTimes,journeyDurations, layovers, flightOperateds)
    
    return len(flightOperateds)

def start_from_a_date():

    elements = driver.find_elements_by_css_selector("span.uitk-tab-text")
    for el in elements:
        if el.text=="Flights":
            el.click()
            break
    oneway=driver.find_element_by_xpath("//*[@id='uitk-tabs-button-container']/div/li[2]/a/span")
    oneway.click()
    driver.find_element_by_xpath("//*[@id='wizard-flight-tab-oneway']/div[2]/div[1]/div/div[1]/div/div/div").click()  ### this is the div
    driver.execute_script("window.scrollTo(0, 50)") 
    
    flyfrom=driver.find_element_by_xpath("//*[@id='location-field-leg1-origin']")
    flyfrom.send_keys(flyFrom + Keys.RETURN)
    
    driver.find_element_by_xpath("//*[@id='wizard-flight-tab-oneway']/div[2]/div[1]/div/div[2]/div/div/div").click()
    driver.find_element_by_xpath("//*[@id='location-field-leg1-destination']").send_keys(flyTo +Keys.RETURN)

    driver.find_element_by_xpath("//*[@id='wizard-flight-tab-oneway']/div[2]/div[2]/div/div/div/div/div").click()

    ### chose date
    #        time.sleep(1)
    # driver.find_element_by_css_selector("button[data-day='16']").click()
    #WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-day='16']"))).click()
    chooseAdate(dateSearch)
    
    #        break
    ### click calendar "done" button
    driver.find_element_by_xpath("//*[@id='wizard-flight-tab-oneway']/div[2]/div[2]/div/div/div/div/div[2]/div/div[3]/button").click()
    
    ### click search
    driver.find_element_by_xpath("//*[@id='wizard-flight-pwa-1']/div[3]/div[2]/button").click()
    
    ###        data-test-id="offer-listing"
    ## feedback button : a data-test-id="goto-opinion-lab-button"
    # nList=len(WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a[data-test-id='goto-opinion-lab-button']"))))
    # lists=driver.find_elements_by_css_selector("li[data-test-id='offer-listing']")
    # print("how many offers: {}, nlist: {}".format(len(lists), nList))
    
    nResult=getData()
    

    
def main():

    global dateSearch
    global oldtime
    global driver
    driver = webdriver.Chrome(options=options, executable_path='../../chromedriver')
    driver.get("https://www.expedia.com")
    driver.maximize_window()
    
    start_from_a_date()

    oldtime=datetime.datetime.now()
    #        rowHeight=141    
    # driver.execute_script("window.scrollTo(0, 640)")
    #        driver.execute_script("window.scrollTo(0, {})".format(540+nPrice*rowHeight)) 
    ###button for each date: (7 in total) li class uitk-date-range-button-wrapper-equal
    
    while True:
        dateSearch+=datetime.timedelta(days=1)
        print("------------a new one ---------{}".format(dateSearch))
        if dateSearch>dateEnd:
            print(" !!!!!! eixt() due to dateSearch>dateEnd)")
            break
            
        ## wait until all 7 buttons shows up -> span class="uitk-date-range-button-date-text"
        
        WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "span.uitk-date-range-button-date-text")))
        
            
        nbutton=len(driver.find_elements_by_css_selector("li.uitk-date-range-button-wrapper-equal"))
        whichday=4
        ### span class="uitk-date-range-button-text"  if the text is "Search", then we have to skip it
        while whichday<7:
            # print("whichday:{}".format(whichday))
            if driver.find_elements_by_css_selector("span.uitk-date-range-button-text")[whichday].text=="Search":
                dateSearch+=datetime.timedelta(days=1)
                whichday+=1
            else:
                break
        if whichday>=7:
            print("!!!!!!!!!!!!!   The next three days all have no tickes to search")
            solve_problem_our_end()                
        else:
            driver.find_elements_by_css_selector("li.uitk-date-range-button-wrapper-equal")[whichday].click()
        nResult=getData()        
        
    outfile.close()
    driver.quit()
    
# def recover():
#     playsound("Simple Sound-tipspc.info.mp3")
#     time.sleep(1)
#     print(" ^^^^^^^^^^^^^^^  going to redo this date and to the end of last day ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
#     print(" ^^^^^^^^^^^^^^^  going to redo this date and to the end of last day ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
#     driver.quit()
#     main()
    
if __name__ == "__main__":
    while True:
        try:
            main()
            break
        except:
            print(" ^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^  error stack->------->______>")
            traceback.print_exc()
            playsound("Simple Sound-tipspc.info.mp3")
            time.sleep(1)
            print(" ^^^^^^^^^^^^^^^  going to redo this date and to the end of last day ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            print(" ^^^^^^^^^^^^^^^  going to redo this date and to the end of last day ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            driver.quit()

#types = [el.text for el in elements]
#print(types)
