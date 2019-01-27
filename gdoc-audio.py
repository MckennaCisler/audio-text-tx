#!/usr/bin/env python
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import pyaudio
import base64
import pyperclip

AUDIO_CHUNK = 6*200
AUDIO_RATE = 5000

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
        ActionChains(self.driver).key_down(Keys.DELETE).perform()

        # use pyperclip
        pyperclip.copy(buf)
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('V').key_up(Keys.CONTROL).perform()


class GDocRX:
    def __init__(self, gdoc):
        self.driver = webdriver.Chrome()
        self.driver.get(gdoc)
        self.editor = self.driver.find_element_by_class_name("kix-page-content-wrapper")

    def __del__(self):
        self.driver.close()

    def get_buf(self, size):
        buf = ""
        while len(buf) < size:
            buf = self.editor.text.replace("\n", "")
            time.sleep(0.01)
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
        encoded = base64.b64encode(raw)
        out_string = str(encoded)+"\n"
        return out_string

    def play_audio_buffer(self, buf):
        raw_frame = eval(buf)
        decoded = bytes(base64.b64decode(raw_frame))
        self.stream.write(decoded)

##### Runner #####

def run_a():
    tx = GDocTX(a_GDOC)
    rx = GDocRX(b_GDOC)
    audio = Audio()
    last_buf=None
    while True:
        # record and send
        tx_buf = audio.rec_audio_buffer()
        # print(tx_buf)
        tx.send_buf(tx_buf)

        #get buf and, if no duplicate, play
        rx_buf = rx.get_buf(AUDIO_CHUNK)
        if(rx_buf!=last_buf):
            audio.play_audio_buffer(rx_buf)

        last_buf=rx_buf # always do at the end of the loop

def run_b():
    tx = GDocTX(b_GDOC)
    rx = GDocRX(a_GDOC)
    audio = Audio()
    last_buf=None
    while True:
        # record and send
        tx_buf = audio.rec_audio_buffer()
        # print(tx_buf)
        tx.send_buf(tx_buf)

        # get buf and, if no duplicate, play
        rx_buf = rx.get_buf(AUDIO_CHUNK)
        if(rx_buf!=last_buf):
            audio.play_audio_buffer(rx_buf)

        last_buf=rx_buf # always do at the end of the loop

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
            # stop recording
            stream.stop_stream()
            stream.close()
            # close PyAudio
            p.terminate()
            print("exiting")

if __name__ == "__main__":
    main()
