from bs4 import BeautifulSoup
import os, random, sys, time
from urllib.parse import urlparse
from urllib.request import urlopen as uReq
from selenium import webdriver


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

browser=webdriver.Chrome()
f=open("Florida Municipalities 10000 or more People.txt","w", )
f.write("Municipality, County\n")
searchPageLink="https://en.wikipedia.org/wiki/List_of_municipalities_in_Florida"
browser.get(searchPageLink)
scroll(browser,1,True,1,2)
table=browser.find_element_by_xpath('//table[@class="wikitable sortable jquery-tablesorter"]').find_element_by_xpath('.//tbody').find_elements_by_xpath('.//tr')
for row in table:
    values=row.find_elements_by_xpath('.//td')
    print(len(values))
    population=values[2].text.replace(",","")
    if int(population)>10000:
        f.write(values[0].find_element_by_xpath('.//a').text.replace(",","")+'\n')
