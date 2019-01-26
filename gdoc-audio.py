#!/usr/bin/env python
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

CHUNK_SIZE = 10
GDOC = "https://docs.google.com/document/d/1uo6DeafeB3qoye25EpZXqZhiRbxN0t63xaQgBrjW1Ng/edit?usp=sharing"

class GDocTX:
    def __init__(self, gdoc):
        self.driver = webdriver.Firefox()
        self.driver.get(gdoc)
        self.txt_element = self.driver.find_element_by_class_name("docs-texteventtarget-iframe")

    def __del__(self):
        self.driver.close()

    def send_buf(self, buf):
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        ActionChains(self.driver).key_down(Keys.DELETE).perform()
        self.txt_element.send_keys(buf)

class GDocRX:
    def __init__(self, gdoc):
        self.driver = webdriver.Firefox()
        self.driver.get(GDOC)
        self.editor = self.driver.find_element_by_class_name("kix-page-content-wrapper")

    def __del__(self):
        self.driver.close()

    def get_buf(self, size):
        buf = ""
        while len(buf) < size:
            buf = self.editor.text
            time.sleep(0.01)
        return buf

##### Audio #####

def rec_audio_buffer():
    return "aaaaaaaaaa"

def play_audio_buffer(buf):
    print(buf)

##### Runners #####

def run_tx():
    tx = GDocTX(GDOC)
    while True:
        buf = rec_audio_buffer()
        tx.send_buf(buf)

def run_rx():
    rx = GDocRX(GDOC)
    while True:
        buf = rx.get_buf(CHUNK_SIZE)
        play_audio_buffer(buf)

def main():
    usage = "usage: ./gdoc-audio.py [tx|rx]"
    if len(sys.argv) != 2:
        print(usage)
    else:
        try:
            side = sys.argv[1]
            if side == "tx":
                run_tx()
            elif side == "rx":
                run_rx()
            else:
                print(usage)
        except KeyboardInterrupt:
            print("exiting")

if __name__ == "__main__":
    main()
