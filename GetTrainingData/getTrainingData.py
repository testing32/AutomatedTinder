from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import urllib
import Image
import csv

def rankmyphotos():
    def getContinue(browser):
        try:
            cont = browser.find_element_by_id('sel_skip')
        except:
            try:
                cont = browser.find_element_by_id('sel_continue')
            except:
                cont = browser.find_element_by_xpath('/html/body/table[3]/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td/div[1]/form/table/tbody/tr/td/table/tbody/tr/td/label/b')
        
        return cont
    
    # open the browser
    browser = webdriver.Firefox()
    
    # navigate to our rating site
    browser.get('http://www.rankmyphotos.com/hotornot.php')
    
    usernames = []
    scores = []
    imageLocations = []
    
    # select women for our pictures
    #elem = browser.find_element_by_id('sel_women')  # Find the search box
    elem = browser.find_element_by_id('sel_men')  # Find the search box
    elem.click()
    
    # we want 10k test images
    for i in range(0, 2000):
        
        try:
            # get the users image
            img = browser.find_element_by_xpath('/html/body/table[3]/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td/img')
            imgurl = img.get_attribute("src")
        except:
            # this sometimes fails
            cont = getContinue(browser)
            cont.click()
            continue
    
        try:
            # vote yes b/c we are a nice scraper
            voteBox = browser.find_element_by_xpath('/html/body/table[3]/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td/div[1]/form/table/tbody/tr/td/table/tbody/tr/td[5]/input')
            voteBox.click()        
        except:
            # if we can't find that element then we need to continue to the next image
            cont = getContinue(browser)
            cont.click()
            continue
            
        # get the username
        username = browser.find_element_by_xpath('/html/body/table[3]/tbody/tr/td/table/tbody/tr/td[3]/table[1]/tbody/tr[3]/td/a').get_attribute('innerHTML')
        
        # we don't want duplicates
        if username in usernames:
            continue
        
        # get the score
        score = browser.find_element_by_xpath('/html/body/table[3]/tbody/tr/td/table/tbody/tr/td[3]/table[1]/tbody/tr[5]/td[2]/span').get_attribute('innerHTML')
        
        # get the labeled data
        usernames.append(username)
        scores.append(score)
        imageLocations.append(imgurl)
        
    # write the labels to a csv file
    with open('trainingData.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for i in range(0, len(usernames)):
            writer.writerow([usernames[i], scores[i]])
    
    
    for i in range(0, len(usernames)):
        urllib.urlretrieve(imageLocations[i], usernames[i]+'.jpg')
 
def buddypic():

    # open the browser
    browser = webdriver.Firefox()
    
    # navigate to our rating site
    browser.get('http://www.buddypic.com')
    
    # rate guys
    browser.find_element_by_xpath('/html/body/div[3]/div[1]/table[2]/tbody/tr/td/div/a[4]').click()
    # rate girls
    #browser.find_element_by_xpath('/html/body/div[3]/div[1]/table[2]/tbody/tr/td/div/a[1]').click()
    
    usernames = []
    scores = []
    imageLocations = []
        
    # we want 10k test images
    for i in range(0, 1000):
        
        # get the username
        username = browser.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr/td/div/center/p[1]/a').get_attribute('innerHTML')
        
        try:
            # get the users image
            img = browser.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr/td/div/center/img')
            imgurl = img.get_attribute("src")
        except:
            # this sometimes fails
            cont = browser.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr/td/div/table/tbody/tr/td[2]/p/a')
            cont.click()
            continue
        
        try:
            # vote 5
            voteBox = browser.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr/td/div/center/form/table/tbody/tr/td[9]/input')
            voteBox.click()
        except:
            # this sometimes fails
            cont = browser.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr/td/div/table/tbody/tr/td[2]/p/a')
            cont.click()
            continue      
        
        # we don't want duplicates
        if username in usernames:
            continue
               
        try: 
            # get the score
            score = browser.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr/td/div/table/tbody/tr/td[1]/table/tbody/tr/td[2]/span').get_attribute('title')
        except:
            # this sometimes fails
            cont = browser.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr/td/div/table/tbody/tr/td[2]/p/a')
            cont.click()
            continue   
        
        # get the labeled data
        usernames.append(username)
        scores.append(score)
        imageLocations.append(imgurl)
        
    # write the labels to a csv file
    with open('trainingData.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for i in range(0, len(usernames)):
            writer.writerow([usernames[i], scores[i]])
    
    
    for i in range(0, len(usernames)):
        urllib.urlretrieve(imageLocations[i], usernames[i]+'.jpg')
        
if __name__ == "__main__":
    #rankmyphotos()
    buddypic()