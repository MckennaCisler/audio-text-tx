from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

driver = webdriver.Firefox()
driver.get("https://docs.google.com/document/d/1uo6DeafeB3qoye25EpZXqZhiRbxN0t63xaQgBrjW1Ng/edit?usp=sharing")

elem = driver.find_element_by_class_name("kix-page-content-wrapper")
while True:
    print(elem.text)
    time.sleep(0.1)

driver.close()
