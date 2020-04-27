from bs4 import BeautifulSoup
import os, random, sys, time
from urllib.parse import urlparse
from urllib.request import urlopen as uReq
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import string

browser=webdriver.Chrome()
actions=ActionChains(browser)

def scroll(browser,fraction,directionDown,pause,segments):
    SCROLL_PAUSE_TIME=pause
    if directionDown:
        for i in range(segments):
            fractionIncrease=fraction*(segments-i)
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight/"+str(fractionIncrease)+");")
            time.sleep(SCROLL_PAUSE_TIME)
    else:
        scrollHeight=int(browser.execute_script("return document.body.scrollHeight"))
        for i in range(segments):
            fractionIncrease=fraction*(segments-i)
            browser.execute_script("window.scrollTo(0,"+str(scrollHeight)+"-(document.body.scrollHeight/"+str(fractionIncrease)+"));")
            time.sleep(SCROLL_PAUSE_TIME)

def seeAll(browser):
    seeAllButtons=browser.find_elements_by_xpath('//button[contains(\
    @class,"pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link link-without-hover-state")]')
    for button in seeAllButtons:
        button.click()


#login
loginLink='https://www.linkedin.com/uas/login'
browser.get(loginLink)
file=open('config.txt','r')
username=file.readline()
password=file.readline()
elementID=browser.find_element_by_id('username')
elementID.send_keys(username)
elementID=browser.find_element_by_id('password')
elementID.send_keys(password)
pageNumber=1 #for quickly skipping pages because changing the html doesn't work
#used later to get each profile based on href
baseProfileLink='https://www.linkedin.com'
searchPageLink="https://www.linkedin.com/search/results/people/?keywords=lion&origin=SWITCH_SEARCH_VERTICAL&page=1" #networking  group
browser.get(searchPageLink)

nextPage=True
startingPage=False
while nextPage:
    if pageNumber==50: #target starting page
        startingPage=True
    if startingPage: #to skip to correct page
        scroll(browser,3/2,True,.1,2)
        searchPageLink=browser.current_url #gets current link to return later
        print(searchPageLink)
        # try:
        #get page and pull html
        src=browser.page_source
        soup=BeautifulSoup(src,'html.parser')
        connectButtons=browser.find_elements_by_xpath('//button[@class="search-result__action-button search-result__actions--primary artdeco-button artdeco-button--default artdeco-button--2 artdeco-button--secondary"]')
        print(len(connectButtons))
        for button in connectButtons:
            count=1
            try:
                #actions.move_to_element(button) #scrollIntoView seems to be just a bit faster, which is better for this program. In general, use move_to_element
                browser.execute_script("arguments[0].scrollIntoView();",button)
                browser.execute_script("scrollBy(0,-300)") #so the element isn't covered by the top header
                button.click()
                doneButton=browser.find_element_by_xpath('//button[@class="ml1 artdeco-button artdeco-button--3 artdeco-button--primary ember-view"]')
                doneButton.click()
                count+=1
            except Exception as e:
                print("Invite already sent")
                #print(e)

    #clicks the next page button after all entries are searched
    found=True
    attempts=0
    scroll(browser,1,True,0,1)
    while found: #loop in case the next button wasn't found because it isn't loaded yet
        try:
            nextPageButton=browser.find_element_by_xpath('//button[@aria-label="Next"]')
            nextPageButton.click()
            found=False
        except:
            print("Button wasn't found, trying again")
            time.sleep(1)
            attempts+=1
    pageNumber+=1
    time.sleep(2) #let page laod
#breaks when finished searching pages
    # except TypeError:
    #     break
