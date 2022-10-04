from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


#Starts our driver and goes to the starting webpage which is google.com
driver = webdriver.Chrome(
    'D:/Universidad/Asignaturas/Taller Ingeniería de Software/scrapping_proyect/chromedriver.exe'
)

driver.get('https://google.com')

#Inputs text into the google search box
input_box = driver.find_element_by_xpath('//*[@id="tsf"]/div[2]/div[1]/div[1]/div/div[2]/input')
input_box.send_keys('top 100 greatest movies of all time imdb')

#Presses the enter button to search
input_box.send_keys(Keys.ENTER)
time.sleep(2)

#Presses on the link for Imdb
press = driver.find_element_by_xpath('//*[@id="rso"]/div[2]/div/div[1]/a/h3').click()

#3 second wait time to let the entire page load in
time.sleep(3)

#Scrolls until Jaws the movie is on the screen
driver.execute_script('window.scrollTo(0,22500)')

#Takes a screenshot of the webpage
driver.save_screenshot('C:\Web Scraping course\jaws.png')

#Takes a screenshot of the Jaws movie poster
driver.find_element_by_xpath('//*[@id="main"]/div/div[4]/div[3]/div[50]/div[1]/a/img').screenshot('D:/Universidad/Asignaturas/Taller Ingeniería de Software/scrapping_proyect/jaws2.png')



