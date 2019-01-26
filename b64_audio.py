import pyaudio
import numpy as np
import base64

# set up pyaudio
CHUNK = 36
RATE = 44100

p=pyaudio.PyAudio()
stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
              frames_per_buffer=CHUNK)


with(open("out.txt",'w')) as f:
    # collect audio
    for i in range(int(5*44100/CHUNK)): #go for a few seconds
        raw = stream.read(CHUNK)
        encoded = base64.b64encode(raw)
        f.write(str(encoded)+"\n")

# stop recording
stream.stop_stream()
stream.close()

#################
# open a stream to write to
stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,output=True,
              frames_per_buffer=CHUNK)

with(open("out.txt",'r')) as f:
    for i in range(int(5*44100/CHUNK)): #go for a few seconds
        raw_frame = eval(f.readline())
        decoded = bytes(base64.b64decode(raw_frame))
        stream.write(decoded)


# stop playing
stream.stop_stream()
stream.close()
p.terminate()
