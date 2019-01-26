#!/usr/bin/env python
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import pyaudio
import base64
import pyperclip

AUDIO_CHUNK = 6*120
AUDIO_RATE = 4000

GDOC = "https://docs.google.com/document/d/1uo6DeafeB3qoye25EpZXqZhiRbxN0t63xaQgBrjW1Ng/edit?usp=sharing"

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
        self.driver.get(GDOC)
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
    def __init__(self, inpt, rate=AUDIO_RATE, chunk_size=AUDIO_CHUNK):
        self.chunk_size = chunk_size
        p = pyaudio.PyAudio()
        if inpt:
            self.stream=p.open(format=pyaudio.paInt16,channels=1,rate=rate,input=True,frames_per_buffer=chunk_size)
        else:
            self.stream=p.open(format=pyaudio.paInt16,channels=1,rate=rate,output=True,
                          frames_per_buffer=chunk_size)

    def __del__(self):
        # stop playing
        self.stream.stop_stream()
        self.stream.close()

    def rec_audio_buffer(self):
        # collect audio
        raw = self.stream.read(self.chunk_size)
        encoded = base64.b64encode(raw)
        out_string = str(encoded)+"\n"
        print(out_string)
        return out_string

    def play_audio_buffer(self, buf):
        raw_frame = eval(buf)
        decoded = bytes(base64.b64decode(raw_frame))
        self.stream.write(decoded)

##### Runners #####

def run_tx():
    tx = GDocTX(GDOC)
    audio = Audio(True)
    while True:
        buf = audio.rec_audio_buffer()
        tx.send_buf(buf)

def run_rx():
    rx = GDocRX(GDOC)
    audio = Audio(False)
    while True:
        buf = rx.get_buf(AUDIO_CHUNK)
        audio.play_audio_buffer(buf)

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
            # stop recording
            stream.stop_stream()
            stream.close()
            # close PyAudio
            p.terminate()
            print("exiting")

if __name__ == "__main__":
    main()
