from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

driver = webdriver.Firefox()
driver.get("https://docs.google.com/document/d/1uo6DeafeB3qoye25EpZXqZhiRbxN0t63xaQgBrjW1Ng/edit?usp=sharing")
ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
ActionChains(driver).key_down(Keys.DELETE).perform()
elem = driver.find_element_by_class_name("docs-texteventtarget-iframe")
while True:
    elem.send_keys("hello world ")
    # ActionChains(driver).send_keys('hello world ').perform()
    time.sleep(1)

driver.close()
