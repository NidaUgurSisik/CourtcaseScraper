headlessMode=False 
delay= 4 #sn
outputcsv= "results.csv"







from re import T, X, search
from sys import displayhook
import cloudscraper
import FileIO
import urllib

from dateutil import rrule
from datetime import date


import urllib
import selenium

from selenium_stealth import stealth
import webdriver_manager
from webdriver_manager.chrome import ChromeDriverManager
import logging
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.keys import Keys
from datetime import timedelta# FOR DEBUG: AŞAĞIDA RRULE İÇİNDEN DE KALDIRMAYI UNUTMA
import os
from selenium.webdriver.support.ui import Select
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#import captchaSolver
from selenium.common.exceptions import ElementNotVisibleException, TimeoutException
from selenium.common.exceptions import NoSuchElementException
from itertools import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

logging.basicConfig(level = logging.INFO)



class Bot:
    driver=None
    START_URL="https://public.courts.in.gov/mycase/#/vw/Search"

    def __init__(self):
        logging.info("bot is starting")

        #WEBDRIVER CONFIG
        chromeDriverPath="./chromedriver.exe"
        options = Options()
        options.add_argument("--log-level=3")
        options.add_argument("--user-data-dir=c:\\temp\\profifgle4205")
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation","test-type"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--disable-gpu')
        options.add_argument("--log-level=3")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/536.36 (KHTML, like Gecko) Chrome/95.0.4664.110 Safari/537.36")
        options.headless = headlessMode
        options.page_load_strategy = 'eager'
        #self.driver = webdriver.Chrome(chromeDriverPath,options=options)
        self.driver= webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
        self.driver.execute_cdp_cmd("Network.enable", {})
        self.driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4663.110 Safari/537.36"}})
       
    def trySolveCaptcha(self):
        xpath='//img[@data-bind="attr: { src: Url }"]'
        self.waitForElementToAppear(xpath)
        src = self.driver.find_element(By.XPATH, xpath).get_attribute("src")
        urllib.request.urlretrieve(src, "aaacaptcha.png")
        result = "asd"#captchaSolver.solveCaptcha("aaacaptcha.png")
        result = result.replace("\n","")
        logging.info("entering captcha: {}".format(result))

        xpath='//input[@id="captchaAnswer"]'
        self.driver.find_element(By.XPATH,xpath).clear()
        self.driver.find_element(By.XPATH,xpath).send_keys(result)

        xpath='//button[@id="captchaContinue"]'
        self.clickElement(xpath)

    def checkIfPopupError(self):
        try:
            errorToast= self.driver.find_element_by_xpath('//div[@class="jq-toast-single jq-has-icon jq-icon-error"]')
            logging.info("got error while reserving:{} ".format(errorToast.text) )
            return True
        except NoSuchElementException as E:
            return False

    def isElementExists(self,xpath):
        try:
            elem= self.driver.find_element(By.XPATH,xpath)
            return True
        except NoSuchElementException as E:
            return False

    def clickElement(self,xpath):
        try:
            self.waitForElementToAppear(xpath,5)
            element=self.driver.find_element(By.XPATH, xpath)
            self.driver.execute_script("arguments[0].click();",element)
        except:
            raise 


    def isCaptcha(self):
        GOT_CAPTCHA = self.isElementExists('//div[@id="CaptchaModal"]') 
        while GOT_CAPTCHA: 
            logging.info("got a captcha.")
            self.trySolveCaptcha()
            time.sleep(4.2451)#TODO: dont wait here
            GOT_CAPTCHA = self.isElementExists('//div[@id="CaptchaModal"]') 
            if GOT_CAPTCHA:
                logging.info("captcha couldnt bypassed. trying again.")
                xpath='//button[@title="Request new image"]'
                self.clickElement(xpath)
            else:
                logging.info("captcha bypassed!")
                return

    def waitForElementToAppear(self,xpath,timeout=15):
        try:
            element_present = EC.presence_of_element_located((By.XPATH, xpath))
            WebDriverWait(self.driver, timeout).until(element_present)  
        except:
            self.isCaptcha()
            raise     

    def waitForElementToDisappear(self,xpath,timeout=15):
        try:
            element_present = EC.invisibility_of_element_located((By.XPATH, xpath))
            WebDriverWait(self.driver, timeout).until(element_present)  
        except:
            self.isCaptcha()
            raise 

    def scrapeSingleCase(self):
        xpath= '//span[@data-bind="html: CaseNumber"]'
        caseNumber= self.driver.find_element(By.XPATH,xpath).text

        xpath= '//span[@data-bind="html: FileDate"]'
        fileDate= self.driver.find_element(By.XPATH,xpath).text

        xpath= '//span[@class="text-muted"][contains(text(),"Status")]/../following-sibling::td'
        status= self.driver.find_element(By.XPATH,xpath).text

        xpath= '//span[contains(text(),"Defendant")]/../../following-sibling::td'
        defendantName= self.driver.find_element(By.XPATH,xpath).text
        
        xpath= '//span[@aria-labelledby="labelPartyAddr"]'
        defendantAdress= self.driver.find_element(By.XPATH,xpath).text

        xpath= '//span[contains(text(),"Plaintiff")]/../../following-sibling::td'
        plaintiffName= self.driver.find_element(By.XPATH,xpath).text

        return [caseNumber, fileDate, status, defendantName,defendantAdress.replace("\n",""), plaintiffName]

    def scrapeResultPage(self):
        try:
            xpath= '//tr[@class="result-row"]'
            self.waitForElementToAppear(xpath)

            results= self.driver.find_elements(By.XPATH,xpath)
            for index in range(len(results)):
                xpath= '//tr[@class="result-row"]'
                result= self.driver.find_elements(By.XPATH,xpath)[index]

                self.driver.execute_script("arguments[0].scrollIntoView();", result)

                xpath= 'td[2]/div[1]/a'#orospcocugu aptal selenium
                caseResultElement=result.find_element(By.XPATH,xpath)
                self.driver.execute_script("arguments[0].click();",caseResultElement)

                xpath= '//span[contains(text(),"Show all party details")]'
                self.waitForElementToAppear(xpath)
                xpath= '//span[contains(text(),"Defendant")]'
                self.clickElement(xpath)


                xpath= '//span[contains(text(),"Plaintiff")]'
                self.clickElement(xpath)

                scrapedCase=self.scrapeSingleCase()   
                FileIO.dosyayaYaz(outputcsv ,",".join(scrapedCase)+"\n")           

                logging.info("scraping done: {}".format(scrapedCase[0]))
                self.driver.back()  
                
                xpath= '//tr[@class="result-row"]'
                self.waitForElementToAppear(xpath)

                time.sleep(delay)

        except BaseException as e:
            logging.error("unexcpected error occured: {}".format(e))

    def scrapeMonth(self,searchTerm):
        try:
            logging.info("getting to search page")
            self.driver.get(self.START_URL)

            logging.info("searching term {}".format(searchTerm))
            xpath='//input[@id="SearchCaseNumber"]'
            self.waitForElementToAppear(xpath)

            self.driver.execute_script("document.body.style.zoom='60%'")
        
            xpath='//input[@id="SearchCaseNumber"]'
            self.driver.find_element(By.XPATH,xpath).clear()
            self.driver.find_element(By.XPATH,xpath).send_keys(searchTerm)

            xpath="//button[contains(text(), 'Search')]"
            self.clickElement(xpath)
            

            xpath='//div[@data-bind="visible: ob.Searching"]'
            self.waitForElementToAppear(xpath)
            self.waitForElementToDisappear(xpath) #captcha çıkınca burda çöküo
            
            

            xpath="//td[contains(text(), 'Search did not match any cases.')]"
            if self.isElementExists(xpath) is True: 
                logging.info("no results found with search term {}".format(searchTerm))
                return

            xpath= '//tr[@class="result-row"]'
            self.waitForElementToAppear(xpath)

            xpath='//span[@data-bind="html: dpager.Showing"]' #POSSIBLE BUG: 2 element could be found
            resultsCount= self.driver.find_element(By.XPATH,xpath).text
            logging.info("scraping {}".format(resultsCount))

            SCRAPE_PAGE=True
            while SCRAPE_PAGE:
                
                self.scrapeResultPage()
                
                xpath='//button[@title="Go to next result page"]'
                SCRAPE_PAGE=self.isElementExists(xpath)
                if SCRAPE_PAGE: 
                    self.clickElement(xpath)
                    time.sleep(0.23133414)

        except BaseException as ex:
            logging.error("error happened: {}".format(ex))
 
    def scrape(self,targetYear=2020, targetMonth=1):
        logging.info("scraping begun")
        datesUntillTarget =list(rrule.rrule(rrule.MONTHLY, dtstart=date(targetYear, targetMonth, 1), until=datetime.now()  - timedelta(days=30) ))[::-1]
        for datee in datesUntillTarget:
            year,month = datee.strftime("%y"), datee.strftime("%m")
            for caseIndex in [1,2,3,4,5,6,7]: #49D01-XXXX-EV*, 49D02-XXXX-EV*, ...
                logging.info("scraping for date {}-{}, case index {}".format(year,month,caseIndex))
                searchTerm= "49D0"+str(caseIndex)+"-"+year+month+"-EV*"
                self.scrapeMonth(searchTerm)
           
    def _check_exists_by_xpath(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True


    def stop(self):
        if (self.driver!=None): 
            self.driver.quit()

    def run(self):
        year,month= input("Please enter year and month number to scrape untill(for example '2020 1' means all cases from this month to untill 1st month of 2020 will be scraped):").split()
        self.scrape(int(year),int(month))
        self.stop()

#DEBUG:
api= Bot()
api.run()
