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
AUDIO_RATE = 4000
# COMPRESS_LEVEL = 9

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

    def get_buf(self):
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

    @staticmethod
    def encode_buf(raw):
        # compressed = bz2.compress(raw, compresslevel=COMPRESS_LEVEL)
        encoded = base64.b64encode(raw)
        return encoded.decode("utf-8") # convert to string

    @staticmethod
    def decode_buf(buf):
        decoded = base64.b64decode(buf)
        return decoded
        # return bz2.decompress(decoded)

##### Runner #####

def run_a(uni=False):
    tx = GDocTX(a_GDOC)
    if uni:
        rx = None
    else:
        rx = GDocRX(b_GDOC)
    audio = Audio()
    run(tx, rx, audio)

def run_b(uni=False):
    if uni:
        tx = None
    else:
        tx = GDocTX(b_GDOC)
    rx = GDocRX(a_GDOC)
    audio = Audio()
    run(tx, rx, audio)

def run(tx, rx, audio):
    p = pyaudio.PyAudio()

    def callback_tx(in_data, frame_count, time_info, status):
        start = time.time()
        tx.send_buf(Audio.encode_buf(in_data))
        print("TX time: %f%%" % (100*(time.time() - start)/(AUDIO_CHUNK/float(AUDIO_RATE))))
        return (in_data, pyaudio.paContinue)

    def callback_rx(in_data, frame_count, time_info, status):
        start = time.time()
        out_data = Audio.decode_buf(rx.get_buf())
        print("RX time: %f%%" % (100*(time.time() - start)/(AUDIO_CHUNK/float(AUDIO_RATE))))
        return (out_data, pyaudio.paContinue)

    # make one stream both input and output - can read and write
    if tx is not None:
        stream_tx = p.open(format=pyaudio.paInt16,channels=1,rate=AUDIO_RATE,input=True, frames_per_buffer=AUDIO_CHUNK, stream_callback=callback_tx)
    if rx is not None:
        stream_rx = p.open(format=pyaudio.paInt16,channels=1,rate=AUDIO_RATE, output=True, frames_per_buffer=AUDIO_CHUNK, stream_callback=callback_rx)

    if tx is not None:
        stream_tx.start_stream()
    if rx is not None:
        stream_rx.start_stream()

    while (tx is not None and stream_tx.is_active()) or \
        (rx is not None and stream_rx.is_active()):
        time.sleep(1)

    if tx is not None:
        stream_tx.stop_stream()
        stream_tx.close()
    if rx is not None:
        stream_rx.stop_stream()
        stream_rx.close()

def main():
    usage = "usage: ./gdoc-audio.py [a|b] [uni|bi]"
    if len(sys.argv) != 3:
        print(usage)
    else:
        try:
            uni = sys.argv[2] == "uni"
            side = sys.argv[1]
            if side == "a":
                run_a(uni=uni)
            elif side == "b":
                run_b(uni=uni)
            else:
                print(usage)
        except KeyboardInterrupt:
            print("exiting")

if __name__ == "__main__":
    main()
