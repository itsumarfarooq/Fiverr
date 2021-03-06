import requests
import os
import sys
import time
import json
import pymongo
from bson.objectid import ObjectId
from selenium import webdriver
from selenium.webdriver.common.proxy import *
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
#from pyvirtualdisplay import Display

#display = Display(visible=0,size=(1024,768))
#display.start()
print("Made a Virtual Display for the browser to run")

myproxy = "10.3.100.207:8080"
proxy = Proxy({
    'proxyType':ProxyType.MANUAL,
    'httpProxy':myproxy,
    'ftpProxy':myproxy,
    'sslProxy':myproxy,
    'noProxy':''
    })
try:
    browser = webdriver.Firefox(proxy=proxy)
    time.sleep(10)
    print("Connection with Firefox Browser Succeeded")
except:
    print("Connection with Firefox Failed")
    sys.exit()

try:
    connection = pymongo.MongoClient()
    db = connection["fiverr_data"]
    gigs = db["gigs"]
    print("Connection with Mongo DB Succeeded")
except:
    print("Connection with Mongo DB Failed. Continuing to store it in a file")

def crawler():
    url = "https://www.fiverr.com/categories/other/"
    browser.get(url)
    time.sleep(10)
    soup = BeautifulSoup(browser.page_source)
    # This is to login into fiverr.com each and every time a new browser opens up

    try:
        a_login = soup('a', text="Sign In")
        url_login = a_login[0]['href']
        print("Connection with Fiverr successfuly made")
    except:
        print("Problem Loading Page. Hence Exiting")
        sys.exit()
    browser.get(url_login)
    time.sleep(10)
    username = browser.find_element_by_class_name("js-form-login")
    username.click()
    username.send_keys("<fiverr_login_id>")
    password = browser.find_element_by_class_name("js-form-password")
    password.click()
    password.send_keys("<fiverr_password>")
    submit = browser.find_element_by_class_name("btn-standard")
    submit.click()
    print("Successfully Logged into Fiverr.com")

    time.sleep(10)
    count = 0
    soup = BeautifulSoup(browser.page_source)
    for link in soup.find_all('a', {'class': 'gig-link-main'}):
        count += 1
        url1 = "https://fiverr.com"+(link.get('href'))
        print("Connecting to the gig "+str(count))
        browser.get(url1)
        try:
            filename = "Others"
            print("Filename is "+filename)
            filename = filename.strip(" ")
            print(filename)
            if not os.path.exists(filename):
                os.makedirs(filename)
            gig_file = open(filename+"/"+str(count)+".txt",'w')
            print("Directory Creation for Storing the file successfull!!")
        except:
            print("Directory Creation Failed")
            gig_file=open(a['href']+"_"+str(count)+".txt",'w')
        

        time.sleep(5)
        i = 1
        print("Entering a loop to load all the comments and reviews")
        while(i > 0):
            try:
                browser.find_element_by_link_text("Show More").click()
            except:
                break
        for i in range(1, 1000):
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        soup = BeautifulSoup(browser.page_source)
        s=""
        favourite= soup.find_all('div',{'class':'gig-collect-count'})
        for d1 in soup.find_all('span', {'class': 'gig-title'}):
            print("Connected to Gig "+(d1.text).strip("\n\t\r"))
            print("Storing the data of this gig in string")
            s+=("{\n\t\"Gig_name\""+": \""+(d1.text).strip("\r\n\t").replace("\"","\\\"")+"\",").encode('utf-8')
        s+=("\n\t").encode('utf-8')
        
        s+=("\"Category\":\"" + ("\"Others\","))
        s+=("\n\t").encode('utf-8')
        
        s+=("\n\t").encode('utf-8')
        
        for span in soup.find_all('span', {'class': 'numeric-rating'}):
            s+=("\"Rating\": \"" + (span.text).strip("\r\n\t").replace("\"","\\\"") + "\",\n\t").encode('utf-8')
        
        for div in soup.find_all('div', {'class': 'gig-main-desc'}):
            s+=("\"Description\":\"" + (div.text).strip("\r\n\t").replace("\"","\\\"") + "\"\t,").encode('utf-8')
        
        for fav in favourite:
            s += ("\"Fourite Count\":\""+(fav.text).strip("\r\n\t")+"\",\n\t").encode('utf-8')
        
        for review_count in soup.find_all('h4',{'itemprop':'reviewCount'}):
            s += ("\"Number of Reviews\":\""+(review_count.text).strip("\r\n\t").replace("\"","\\\"")+"\",\n\t").encode('utf-8')
        data2 = soup.find_all('ul', {'class': 'reviews-list'})
        
        count_review = 1
        for ul2 in data2:
            s+=("\"Reviews\":["). encode('utf-8')
        
            for li2 in ul2.find_all('li'):
                linkss = li2.find_all('a')
                divi = li2.find_all('div', {'class':'msg-body'})
                spann = li2.find_all('span', {'class': 'rating-date'})
                count_r = 0
                for a2 in linkss:
                    s+=("\n\t\t\t{\n\t\t\t\t\"User\":\""+(a2.text).strip("\r\n\t").replace("\"","\\\"")+"\",").encode('utf-8')
                    s+=("\n\t\t\t\t").encode('utf-8')

                    s+=("\"Message\":\""+(divi[count_r].text).strip("\r\n\t").replace("\"","\\\"")+"\",").encode('utf-8')
                    s+=("\n\t\t\t\t").encode('utf-8')

                    s+=("\"Rating-Date\":\""+(spann[count_r].text).strip("\r\n\t").replace("\"","\\\"")+"\"\n\t\t\t},").encode('utf-8')
                    count_r += 1
                time.sleep(1)
        s = s[:-1]
        s+=("\n\t]").encode('utf-8')
        s+=("\n}").encode('utf-8')
        print("Formatting the data to be stored into database")
        s = s.strip(" ")
        s = s.replace("\r","")
        s = s.replace("\n","")
        print("Formatting the data done")
        gig_file.write(s)
        gig_file.close()
        try:
            gigs.insert_one(json.loads(s))
            print("Storing the above gig Successfull!!")
        except:
            print("Storing the above gig failed!!")
            pass
        print("Stored in the MongoDB. proceeding on the another gig if it exists!!")
crawler()
