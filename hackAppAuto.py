from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import requests
import json

hackathons = {"test" : "https://docs.google.com/forms/d/17INdLqg8Nw05nU1cqJEAv7f1q6VBcfUEmCoehvQo6gw/viewform?c=0&w=1","Whacks" : "https://docs.google.com/forms/d/14b0LJ9s3oJ2SwS75iJ91VK3Quo8kFfMVu8TSBjAv8sQ/viewform"}
''' 
fields = OrderedDict([
    ("Name? ", "#entry_692178301"), 
    ("College? ", "#entry_1519264832"), 
    ("Email? ", "#entry_7249939"), 
    ("Phone? ", "#entry_156205721"), 
    ("Year? (first, sophomore,junior, senior) ", "#ss-form > ol > div:nth-child(7) > div > div > ul > li"), 
    ("Hackathon Goals? ",  "#entry_1829884217"),
    ("Areas of Interests? ", "#entry_2072654321"), 
    ("Link to your Resume? ", "#entry_450984524"),
    ("Allergies? ", "#entry_388506799"), 
    ("Accept Code of Conduct? ", "#group_2031524162_1"),
    ("Are you sure you want to submit? Y/N ", "#ss-submit")
])
'''
fields = OrderedDict([
    ("What is your name? ", "#entry_1211499755"),
    ("What is your email? ", "#entry_1853212604"),
    ("What are your interests? ", "#entry_512697689"),
    ("Submit form? (yes/no)", "#ss-submit")
])

def getQuestions():
    q = []
    for key in fields:
        q.append(key)
    print q
    return q

def submitForm(answers):

    driver = webdriver.PhantomJS()
    driver.get(hackathons["test"])
    count = 0
    for k in fields:
        curr = driver.find_element_by_css_selector(fields[k])
        if not count == 3:
            curr.send_keys(answers[count])
        else:
            curr.click()
        count += 1
    print "Submitted!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    driver.quit()

def useAPI(name):
    theURL = "http://hackathon.qw3rty01.com/api/v0.1/form?name=" + name
    attrReq = requests.get(theURL).content
    attrReq = json.loads(attrReq)

    return attrReq

def getQuestionsAuto(name):
    getData = useAPI(name)
    fields = getData["value"]["children"]
    questions = []
    for i in range(0, len(fields)):
        questions.append(fields[str(i)]["name"] + "? ")

    return questions
    
def submitFormAuto(answers, name):
    driver = webdriver.PhantomJS()
    getData = useAPI(name)
    
    driver.get(getData["value"]["url"])
    fields = getData["value"]["children"]
    count = 0
    for i in range(0, len(fields)):
        curr = driver.find_element_by_name(fields[str(i)]["tagname"])
        if fields[str(i)]["type"] == "text":
            curr.send_keys(answers[count])
        else:
            curr.click()
        count += 1
    
'''
FOR WHACKS
def submitForm(answers):
    
    count = 0
    for k in fields:
        curr = driver.find_element_by_css_selector(fields[k])
        if not count in [4,9,10]:
            curr.send_keys(answers[count])
        elif count == 4:
            for year in curr:
                if answer.lower().strip() in year.text.lower():
                    radioButton = year.find_element_by_class_name("ss-q-radio")
                    radioButton.click()
                    print "Success"
        elif count == 9:
            curr.click()
        else:
            curr.click()
            print "Submitted Successfully!"
'''
