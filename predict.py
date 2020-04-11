import sounddevice as sd
from scipy.io.wavfile import write
import pylab
import wave
from PIL import Image
import numpy as np
import tensorflow.keras as keras


def graph_spectrogram(wav_file):
    sound_info, frame_rate = get_wav_info(wav_file)
    un,d,t,im = pylab.specgram(sound_info, Fs=frame_rate)
    im = Image.fromarray(un)
    print(len(d))
    print(len(t))
    print(len(un))
    if im.mode != 'RGB':
        im = im.convert('1')
    im.save("test.png")
    return im
def get_wav_info(wav_file):
    wav = wave.open(wav_file, 'r')
    frames = wav.readframes(-1)
    sound_info = pylab.fromstring(frames, 'Int16')
    frame_rate = wav.getframerate()
    wav.close()
    return sound_info, frame_rate



fs = 8000  # Sample rate
seconds = 1  # Duration of recording
model = keras.models.load_model("80p_prop_unk.h5")

while 1:
    inp = input("Type 'r' to record: ")
    if inp=="r":
        myrecording = sd.rec(np.int16(seconds * fs), samplerate=fs, channels=2, dtype='int16')
        sd.wait()  # Wait until recording is finished
        write('output.wav', fs, myrecording)  # Save as WAV file
        im = graph_spectrogram('output.wav')
        im = np.array(im)
        im = im.reshape((1, 129, 124, 1))
        # output = rd.choice(np.identity(11)[2:]) #ligne a supprimer une fois le réseau raccordé
        output = model.predict(im) #sort un vecteur de probas de taille 11
        classes = ["<UNK>","no", "on", "go", "up", "stop", "off", "left", "right", "down", "yes"]
        #commands = [('unknown',), ('no',), ('on',), ('go',), ('up', ), ('stop',), ('off', ), ('left',), ('right', ), ('down', ), ('yes', )]
        out = classes[np.argmax(output)]
        print("\n" + out + "\n")
        inp = "no"