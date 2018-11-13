import pyaudio
import numpy as np
import wave
import matplotlib.pyplot as plt
import threading

def generateSine(volume=0.5, fs=44100, duration=1.0, f=440.0):
	p = pyaudio.PyAudio()

	# volume = 0.5     # range [0.0, 1.0]
	# fs = 44100       # sampling rate, Hz, must be integer
	# duration = 1.0   # in seconds, may be float
	# f = 440.0        # sine frequency, Hz, may be float

	# generate samples, note conversion to float32 array
	samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)

	# for paFloat32 sample values must be in range [-1.0, 1.0]
	stream = p.open(format=pyaudio.paFloat32,
	                channels=1,
	                rate=fs,
	                output=True)

	# play. May repeat with different volume values (if done interactively) 
	stream.write(volume*samples)

	stream.stop_stream()
	stream.close()

	p.terminate()

def record():
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 44100
	CHUNK = 1024
	RECORD_SECONDS = 5
	WAVE_OUTPUT_FILENAME = "file.wav"
	 
	p = pyaudio.PyAudio()
	 
	# start Recording
	streamrec = p.open(
						format=FORMAT,
						channels=CHANNELS,
					    rate=RATE, 
					    input=True,
					    frames_per_buffer=CHUNK)
	print("recording...")
	frames = []

	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	    data = streamrec.read(CHUNK)
	    # print(data)
	    frames.append(data)
	print("finished recording")

	# print(frames) 
	 
	# stop Recording
	streamrec.stop_stream()
	streamrec.close()
	p.terminate()

	# plotlist = []
	# for each in frames:
	#     # print(each)
	#     amplitude = np.fromstring(each, np.int16)
	#     plotlist.append(amplitude)
	# plotlist = np.concatenate(plotlist).ravel().tolist()



	# plt.plot(plotlist,'.')
	# plt.show()

	# #berechnet rms 
	# rms = np.sqrt(np.mean(np.square(plotlist)))
	# print(rms)

def drucken():
	print('ich drucke hier was')

gs = threading.Thread(target=generateSine)
wr = threading.Thread(target=record)
t3 = threading.Thread(target=drucken)
# t3.start()
# f1.append(f1)
# f2.append(f2)
gs.start()
# t2.start()
wr.start()
t3.start()


