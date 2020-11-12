from bs4 import BeautifulSoup
import os, random, sys, time
from urllib.parse import urlparse
from urllib.request import urlopen as uReq
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import string
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="http")

browser=webdriver.Chrome()
mode="w"

class LinkedinScraperMap:
    def __init__(self):
        def newMunicipalityFile(cityName):
            f=open(cityName.replace('\n',"")+".csv",mode,1) #one line buffering so no explicit flush call is needed
            if mode=="w":
                headers="Name,Location,Interests\n"
                f.write(headers)
            return f

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
            try:
                #while True: #keeps checking in case there are nested buttons
                seeAllButtons=browser.find_elements_by_xpath('//button[contains(\
                @class,"pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link link-without-hover-state")]')
                for button in seeAllButtons:
                    browser.execute_script("arguments[0].scrollIntoView();",button)
                    browser.execute_script("scrollBy(0,-200)") #so the element isn't covered by the top header
                    button.click()
            except:
                print('No more buttons')

        #login
        loginLink='https://www.linkedin.com/uas/login'
        browser.get(loginLink)
        loginData=open('config.txt','r')
        username=loginData.readline()
        password=loginData.readline()
        elementID=browser.find_element_by_id('username')
        elementID.send_keys(username)
        elementID=browser.find_element_by_id('password')
        elementID.send_keys(password)
        #browser.find_element_by_xpath('//button[@class="btn__primary--large from__button--floating"]').click() #I'm not sure why, but this automatically submits

        #get municipalities to search for

        municipalities=open('Florida Municipalities 10000 or more People.txt','r')
        recordedProfiles=0
        pageNumber=1 #used to skip ahead pages because changing link doesn't work.
        baseProfileLink='https://www.linkedin.com'
        #link that will be searched


        nextPage=True
        startingPage=False
        nextCity=True
        while nextCity:
            municipalityName=municipalities.readline().strip(" ")
            print(municipalityName)
            f=newMunicipalityFile(municipalityName)
            searchPageLink='https://www.linkedin.com/search/results/people/?keywords='\
+municipalityName.replace(' ','%20')+'&origin=GLOBAL_SEARCH_HEADER'
            browser.get(searchPageLink)
            try: #should fail only when program went through all people
                while nextPage:
                    if pageNumber==1: #target starting page
                        startingPage=True
                    if startingPage: #bypasses this block until we're at the first desired page
                        scroll(browser,1,True,0,1)
                        searchPageLink=browser.current_url
                        print(searchPageLink)
                        # try:
                        #get page and pull html
                        src=browser.page_source
                        soup=BeautifulSoup(src,'html.parser')
                        profileContainers=soup.find_all('li',{'class':'search-result search-result__occluded-item ember-view'})
                        visibleProfiles=[]
                        links=[]
                        for container in profileContainers:
                            private=False
                            nameSearch=container.find('span',{'class':'actor-name'}).text
                            #check if member is visible, go to page if possible(name is "LinkedIn Member" if not private)
                            if nameSearch!="LinkedIn Member":
                                visibleProfiles.append(container)
                                links.append(container.div.div.div.a['href'])
                        print(len(profileContainers))
                        for link in links:
                            print(str(link))
                            #dealing with each container
                        for profile in visibleProfiles:
                            loadingError=True
                            userLink=links[visibleProfiles.index(profile)]
                            browser.get(baseProfileLink+userLink)
                            while loadingError:#occasional errors with dynamic loading of pages, sets to False at the end of each profile
                                try:
                                    #goes to each profile
                                    profile_src=browser.page_source
                                    soup=BeautifulSoup(profile_src,'html.parser')
                                    profile_src=browser.page_source
                                    soup=BeautifulSoup(profile_src,'html.parser')
                                    #Name and Location
                                    name_div = soup.find('div', {'class': 'flex-1 mr5'})
                                    #location
                                    locationAvailable=True
                                    try:
                                        name_loc = name_div.find_all('ul')
                                        locationString=name_loc[1].find('li').get_text().strip()
                                        locator=geolocator.geocode(locationString)
                                        location=(locator.latitude,locator.longitude)
                                    except:
                                        location='N/A'
                                        locationAvailable=False


                                    #if not location, then don't get interests. Don't record in file. Saves ~4-5 seoncds every profile
                                    if locationAvailable:
                                        #name
                                        try:
                                            name = name_loc[0].find('li').get_text().strip()
                                        except:
                                            name='N/A'

                                        #INTERESTS
                                        interests=''
                                        browser.get(baseProfileLink+userLink+'/detail/interests/companies/')
                                        # seeAllInterestsButton=browser.find_element_by_xpath('//a[@class="pv-profile-section__card-action-bar artdeco-container-card-action-bar artdeco-button artdeco-button--tertiary artdeco-button--3 artdeco-button--fluid ember-view"]')
                                        # seeAllInterestsButton.click()
                                        time.sleep(1)
                                        notLoaded=True
                                        count=0
                                        while notLoaded:
                                            try:
                                                interestsTab=browser.find_element_by_xpath('//div[@class="artdeco-modal artdeco-modal--layer-default  pv-interests-modal pv-profile-detail__modal pv-profile-detail__modal--v2"]')
                                                notLoaded=False
                                            except:
                                                count+=1
                                                if count>50:
                                                    count=0
                                                    break
                                                print("Interests haven't loaded yet. Trying again")
                                                time.sleep(1)
                                        #max possible 4 different categories of interests: Influencers, Groups, Companies, and Schools
                                        categories=browser.find_elements_by_xpath('//a[@class="pv-profile-detail__nav-link t-14 t-black--light t-bold ember-view"]')
                                        try:
                                            for category in categories:
                                                category.click()
                                                time.sleep(1)
                                                notLoaded=True
                                                while notLoaded:
                                                    try:
                                                        interestsList=interestsTab.find_element_by_xpath('.//div[@class="entity-all pv-interests-list ember-view"]')
                                                        notLoaded=False
                                                    except:
                                                        time.sleep(1)
                                                        print("not loaded")
                                                interestsContainer=interestsList.find_elements_by_xpath('.//li[@class=" entity-list-item"]')
                                                for interest in interestsContainer:
                                                    interests+=interest.find_element_by_xpath('.//span[@class="pv-entity__summary-title-text"]').text+'.'
                                        except Exception as e:
                                            print(e)
                                            interests='N/A'
                                        if interests != 'N/A' and interests!='':
                                            lastEntry=''
                                            if lastEntry!='':
                                                lastEntry=entry
                                            entry=(
                                                 str(name).replace(",","")+','+str(location).replace(',',' . ')+','+str(interests).replace(",","")
                                            )
                                        print(entry)
                                        #string.printable had characters that I didn't want that couldn't be removed
                                        printable="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ "
                                        if lastEntry!=entry:
                                            for char in entry: #saves only characters that are printable recognized from string printable function
                                                if printable.find(char)!=-1:
                                                    f.write(char)
                                            f.write('\n')
                                            recordedProfiles+=1
                                            print(str(recordedProfiles))
                                    loadingError=False
                                except Exception as e:
                                    print("Error in getting page data on page "+baseProfileLink+userLink)
                                    print(e)
                    #clicks the next page button after all entries are searched
                    browser.get(searchPageLink)
                    scroll(browser,1,True,0,1)
                    notNewPage=True
                    while notNewPage: #loop in case the next button wasn't found because it isn't loaded yet or is covered by another element
                        try:
                            nextPageButton=browser.find_element_by_xpath('//button[@aria-label="Next"]')
                            nextPageButton.click()
                            time.sleep(2)
                            notNewPage=False
                        except Exception as e:
                            print(e)
                            print("Button wasn't found, trying again")
                            time.sleep(1)
                            browser.execute_script("scrollBy(0,300)") #scrolls past blocking element(usually a chatbox)
                    if searchPageLink==browser.current_url:
                        raise TypeError("Completed search for current municipality. Break to go to next one")
                    pageNumber+=1
                    if pageNumber%20==0: #pause every 20 pages for 3 minutes to avoid being force logged out
                        time.sleep(180)
                        print('Pause over, continuing to scrape')
                    #time.sleep(2) #let page laod
            except TypeError as e: #went through all
                print("Last Page: "+str(pageNumber))
                print(e)
                f.close()
            except Exception as e:
                #method needed to restart if something goes really wrong so I can get the last page visited
                print("Something unexpectedly went wrong")
                print("Last Page: "+str(pageNumber))
                print(e)
                break
            # #breaks when finished searching pages
                # except TypeError:
                #     break
linkedinscrape=LinkedinScraperMap()
