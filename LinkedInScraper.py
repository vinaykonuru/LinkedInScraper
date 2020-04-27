from bs4 import BeautifulSoup
import os, random, sys, time
from urllib.parse import urlparse
from urllib.request import urlopen as uReq
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import string

browser=webdriver.Chrome()
mode="w"
f=open("MidWood Highschool Scrape.csv",mode,1) #one line buffering so no explicit flush call is needed
if mode=="w":
    headers="Name,Title,Undergraduate College,Degree Year,Major,Stream,\
Terminal College,Terminal Degree Year,Terminal Major,Terminal Stream,\
Location,Current Job Title,Current Company,Join Date,Experience,First Listed Job Title,\
First Listed Company,First Company Join Date,First Company Experience\n"
    f.write(headers)


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
file=open('config.txt','r')
username=file.readline()
password=file.readline()
elementID=browser.find_element_by_id('username')
elementID.send_keys(username)
elementID=browser.find_element_by_id('password')
elementID.send_keys(password)
browser.find_element_by_xpath('//button[@class="btn__primary--large from__button--floating"]').click()
pageNumber=1 #used to skip ahead pages because changing link doesn't work.
baseProfileLink='https://www.linkedin.com'
#link that will be searched
searchPageLink="https://www.linkedin.com/search/results/people/?facetPastCompany=%5B%2227070962%22%2C%224360%22%5D&keywords=midwood%20high%20School&origin=FACETED_SEARCH"
browser.get(searchPageLink)

nextPage=True
startingPage=False
try:
    while nextPage:
        scroll(browser,1,True,1,2)
        if pageNumber==1: #target starting page
            startingPage=True
        if startingPage: #bypasses this block until we're at the first desired page
            searchPageLink=browser.current_url #gets current link to return later
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
            for container in visibleProfiles:
                    userLink=links[visibleProfiles.index(container)]
                    browser.get(baseProfileLink+userLink)
                    profile_src=browser.page_source
                    soup=BeautifulSoup(profile_src,'html.parser')
                    #scroll to bottom, check if there are "see more" buttons, click, and scroll back to the top to load
                    try:
                        scroll(browser,1,True,1,2)
                        seeAll(browser)
                        seeAll(browser) #twice because of seeAll button inside of another seeAll button
                        scroll(browser,1,False,1,2)
                        profile_src=browser.page_source
                        soup=BeautifulSoup(profile_src,'html.parser')
                    except Exception as e:
                        print("No 'see all experiences' button")
                        print(e)
                    #Name and Location
                    name_div = soup.find('div', {'class': 'flex-1 mr5'})
                    name_loc = name_div.find_all('ul')
                    #name
                    try:
                        name = name_loc[0].find('li').get_text().strip()
                    except:
                        name="N/A"
                    #location
                    try:
                        location = name_loc[1].find('li').get_text().strip()
                    except:
                        location="N/A"
                    #title
                    try:
                        profile_title = name_div.find('h2').get_text().strip()
                    except:
                        profile_title="N/A"
                    connection = name_loc[1].find_all('li')
                    #connections
                    try:
                        numberOfConnections = connection[1].get_text().strip()
                    except:
                        connection="N/A"

                    #Experience- now it's easier to get all experiences if required
                    try:
                        exp_container=browser.find_elements_by_xpath('//li[@class="pv-entity__position-group-pager pv-profile-section__list-item ember-view"]')
                    except:
                        print("Error in experience section")
                    for x, e in enumerate(exp_container):
                        a_tags = exp_container[x]
                        try:
                            companySpecifics=a_tags.find_element_by_xpath('.//ul[@class="pv-entity__position-group mt2"]')
                            specifics=True
                        except:
                            specifics=False
                        #JOB
                        try:
                            if specifics:
                                jobsAtCompany=companySpecifics.find_elements_by_xpath('.//h3[@class="t-16 t-black t-bold"]')
                                if x==0:
                                    jobTitle=jobsAtCompany[-1] #most recent job
                                elif x==len(exp_container)-1:
                                    jobTitle=jobsAtCompany[0]  #first job
                            else:
                                jobTitle=a_tags.find_element_by_xpath('.//h3[@class="t-16 t-black t-bold"]').text.strip()
                            if x==0:
                                final_job_title = jobTitle
                            if x==(len(exp_container)-1):
                                first_job_title = jobTitle
                        except Exception as e:
                            if x==0:
                                final_job_title="N/A"
                            if x==(len(exp_container)-1):
                                first_job_title="N/A"
                        #COMPANY NAME
                        try:
                            if specifics:
                                companyName=a_tags.find_element_by_xpath('.//h3[@class="t-16 t-black t-bold"]').find_elements_by_xpath('.//*')[1].text.strip()
                            else:
                                companyName=a_tags.find_element_by_xpath('.//p[@class="pv-entity__secondary-title t-14 t-black t-normal"]').text.strip()
                            if x==0:
                                final_company_name=companyName
                            if x==(len(exp_container)-1):
                                first_company_name=companyName
                        except Exception as e:
                            if x==0:
                                final_company_name="N/A"
                            if x==(len(exp_container)-1):
                                first_company_name="N/A"
                        #DATES IN JOB
                        try:
                            if specifics:
                                dates=companySpecifics.find_elements_by_xpath('.//h4[@"pv-entity__date-range t-14 t-black--light t-normal"]')
                                if x==0: #simpified way to get real first job and latest job
                                    joiningDate=dates[0]
                                elif x==len(exp_container-1):
                                    joiningDate=dates[-1]
                            else:
                                joiningDate=a_tags.find_element_by_xpath('.//h4[@class="pv-entity__date-range t-14 t-black--light t-normal"]')
                            date=joiningDate.find_elements_by_xpath('.//*')[1].text.strip()
                            if x==0:
                                final_joining_date=date
                            if x==(len(exp_container)-1):
                                first_joining_date=date
                        except Exception as e:
                            if x==0:
                                final_joining_date="N/A"
                            if x==(len(exp_container)-1):
                                first_joining_date="N/A"
                        #TOTAL TIME IN COMPANY IN ALL JOBS
                        try:
                            experience=a_tags.find_element_by_xpath('.//span[@class="pv-entity__bullet-item-v2"]').text.strip()
                            if x==0:
                                final_exp=experience
                            if x==(len(exp_container)-1):
                                first_exp=experience
                        except Exception as e:
                            if x==0:
                                final_exp="N/A"
                            if x==(len(exp_container)-1):
                                first_exp="N/A"

                    #Education- now it's easier to get all educational affiliations if required
                    try:
                        edu_container=browser.find_elements_by_xpath('//li[@class="pv-profile-section__list-item pv-education-entity pv-profile-section\
                        __card-item ember-view"]')
                    except:
                        print("Error in education section")
                    for x in range(len(edu_container)):
                        a_tags = edu_container[x]
                        try:
                            collegeName=a_tags.find_element_by_xpath('.//h3[@class="pv-entity__school-name t-16 t-black t-bold"]').text.strip()
                            if x==0:
                                final_college_name=collegeName
                            if x==(len(edu_container)-1):
                                first_college_name=collegeName
                        except Exception as e:
                            if x==0:
                                final_college_name="N/A"
                            if x==(len(edu_container)-1):
                                first_college_name="N/A"
                        try:
                            degreeName=a_tags.find_element_by_xpath('.//span[@class="pv-entity__comma-item"]').text.strip()
                            if x==0:
                                final_degree_name=degreeName
                            if x==(len(edu_container)-1):
                                first_degree_name=degreeName
                        except Exception as e:
                            if x==0:
                                final_degree_name="N/A"
                            if x==(len(edu_container)-1):
                                first_degree_name="N/A"
                        try:
                            stream=a_tags.find_element_by_xpath('.//span[@class="pv-entity__comma-item"]').text.strip()
                            if x==0:
                                final_stream=stream
                            if x==(len(edu_container)-1):
                                first_stream=stream
                        except Exception as e:
                            if x==0:
                                final_stream="N/A"
                            if x==(len(edu_container)-1):
                                first_stream="N/A"
                        try:
                            degreeYearList=a_tags.find_element_by_xpath('.//p[@class="pv-entity__dates t-14 t-black--light t-normal"]')\
                            .find_elements_by_xpath('.//*')[1].find_elements_by_xpath(".//*")
                            degreeYear=degreeYearList[0].text.strip()+"-"+degreeYearList[1].text.strip()
                            if x==0:
                                final_degree_year=degreeYear
                            if x==(len(edu_container)-1):
                                first_degree_year=degreeYear
                        except Exception as e:
                            if x==0:
                                final_degree_year="N/A"
                            if x==(len(edu_container)-1):
                                first_degree_year="N/A"


                    #writes all data to file
                    entry=(
                         str(name).replace(",","")+","+str(profile_title).replace(",","")+","+(first_college_name).replace(",","")\
                    +","+str(first_degree_year).replace(",","")+","+str(first_degree_name).replace(",","")+","+str(first_stream).replace(",","")\
                    +","+str(final_college_name).replace(",","")+","+str(final_degree_year).replace(",","")+","+str(final_degree_name).replace(",","")\
                    +","+str(final_stream).replace(",","")+","+str(location).replace(",","")+","+str(final_job_title).replace(",","")\
                    +","+str(final_company_name).replace(",","")+","+str(final_joining_date).replace(",","")+","+str(final_exp).replace(",","")\
                    +","+str(first_job_title).replace(",","")+","+str(first_company_name).replace(",","")+","+str(first_joining_date).replace(",","")\
                    +","+str(first_exp).replace(",","")
                    )
                    print(entry)
                    printable=string.printable
                    for char in entry: #saves only characters that are printable recognized from string printable function
                        if printable.find(char)!=-1:
                            f.write(char)
                    f.write('\n')
        #clicks the next page button after all entries are searched
        browser.get(searchPageLink)
        scroll(browser,1,True,0,1)
        found=True
        while found: #loop in case the next button wasn't found because it isn't loaded yet or is covered by another element
            try:
                nextPageButton=browser.find_element_by_xpath('//button[@aria-label="Next"]')
                nextPageButton.click()
                found=False
            except:
                print("Button wasn't found, trying again")
                time.sleep(1)
                browser.execute_script("scrollBy(0,300)")
        pageNumber+=1
        time.sleep(2) #let page laod
except Exception as e:
    print("Last Page: "+str(pageNumber))
    print(e)
#breaks when finished searching pages
    # except TypeError:
    #     break
