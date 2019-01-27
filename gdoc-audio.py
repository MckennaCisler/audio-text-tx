#!/usr/bin/env python
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import pyaudio
import base64
import pyperclip
import bz2

MIN_BASE64_CHARS = 4
AUDIO_CHUNK = MIN_BASE64_CHARS*1200
AUDIO_RATE = 4800
COMPRESS_LEVEL = 1

a_GDOC = "https://docs.google.com/document/d/1pIDWZmBUX7o7hK0ZYNKAqoFRroX8rLYvFEeF-bSz2L4/edit?usp=sharing"
b_GDOC = "https://docs.google.com/document/d/1HiNo-zLW-M6RK4mEri7Zsdb7RzWgF_U_P9vCQoP44-g/edit?usp=sharing"

class GDocTX:
    def __init__(self, gdoc):
        # init selenium things
        self.driver = webdriver.Chrome()
        self.driver.get(gdoc)
        self.txt_element = self.driver.find_element_by_class_name("docs-texteventtarget-iframe")

    def __del__(self):
        # close selenium
        self.driver.close()

    def send_buf(self, buf):
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        # ActionChains(self.driver).key_down(Keys.DELETE).perform()

        # use pyperclip
        pyperclip.copy(buf)
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('V').key_up(Keys.CONTROL).perform()


class GDocRX:
    def __init__(self, gdoc):
        self.driver = webdriver.Chrome()
        self.driver.get(gdoc)
        self.editor = self.driver.find_element_by_class_name("kix-zoomdocumentplugin-outer")

    def __del__(self):
        self.driver.close()

    def get_buf(self, size):
        buf = self.editor.text
        buf = buf.replace("\n", "")
        buf = buf.replace(" ", "")
        # ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        # ActionChains(self.driver).key_down(Keys.DELETE).perform()
        return buf


class Audio:
    def __init__(self, rate=AUDIO_RATE, chunk_size=AUDIO_CHUNK):
        self.chunk_size = chunk_size
        p = pyaudio.PyAudio()
        # make one stream both input and output - can read and write
        self.stream=p.open(format=pyaudio.paInt16,channels=1,rate=rate,input=True, output=True, frames_per_buffer=chunk_size)

    def __del__(self):
        # stop playing
        self.stream.stop_stream()
        self.stream.close()

    def rec_audio_buffer(self):
        # collect audio
        raw = self.stream.read(self.chunk_size)
        compressed = bz2.compress(raw, compresslevel=COMPRESS_LEVEL)
        encoded = base64.b64encode(compressed)
        return encoded.decode("utf-8") # convert to string

    def play_audio_buffer(self, buf):
        # # make sure 6-aligned
        # extra = len(buf) % MIN_BASE64_CHARS
        # if extra != 0:
        #     addons = "0"*(MIN_BASE64_CHARS-extra)
        # else:
        #     addons = ""
        decoded = base64.b64decode(buf)
        decompressed = bz2.decompress(decoded)
        self.stream.write(decompressed)

##### Runner #####

def run_a():
    tx = GDocTX(a_GDOC)
    rx = GDocRX(b_GDOC)
    audio = Audio()
    run(tx, rx, audio)

def run_b():
    tx = GDocTX(b_GDOC)
    rx = GDocRX(a_GDOC)
    audio = Audio()
    run(tx, rx, audio)

def run(tx, rx, audio):
    while True:
        # record and send
        tx_buf = audio.rec_audio_buffer()
        tx.send_buf(tx_buf)

        # get buf and play
        rx_buf = rx.get_buf()
        audio.play_audio_buffer(rx_buf)

def main():
    usage = "usage: ./gdoc-audio.py [a|b]"
    if len(sys.argv) != 2:
        print(usage)
    else:
        try:
            side = sys.argv[1]
            if side == "a":
                run_a()
            elif side == "b":
                run_b()
            else:
                print(usage)
        except KeyboardInterrupt:
            print("exiting")

if __name__ == "__main__":
    main()
