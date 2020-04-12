import sounddevice as sd
from scipy.io.wavfile import write
import pylab
import wave
from PIL import Image
import numpy as np
import tensorflow.keras as keras
from spectro import graph_spectrogram
import cv2

# Set parameters
fs = 16000  # Sample rate
seconds = 1  # Duration of recording
model = keras.models.load_model("models/86p_no_unk.h5")

# Given au audio track, predicts the output
def prediction(myrecording, model):
    file = 'tmp/output.wav'
    write(file, fs, myrecording)  # Save as WAV file
    graph_spectrogram(file, 1)
    im = cv2.imread('tmp/output.png', 0)
    image = np.array([np.asarray(im)])
    to_pred = image.reshape((1, 129, 124, 1))
    # output = rd.choice(np.identity(11)[2:]) #ligne a supprimer une fois le réseau raccordé
    output = model.predict(to_pred) #sort un vecteur de probas de taille 11
    classes = ["no", "on", "go", "up", "stop", "off", "left", "right", "down", "yes", "<UNK>"]
    #commands = [('unknown',), ('no',), ('on',), ('go',), ('up', ), ('stop',), ('off', ), ('left',), ('right', ), ('down', ), ('yes', )]
    print(np.around(output[0], decimals=3))
    out = classes[np.argmax(output)]
    return out

# Records 1s of andio and then predicts
def rec_and_predict():
    myrecording = sd.rec(seconds * fs, samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    print("REC STOP")
    return prediction(myrecording)


# DEMO
# Uncomment if you wanna try
"""
while 1:
    inp = input("Type 'r' to record for 1s: ")
    if inp!="idk":
        out = rec_and_predict()
        print(out)
        inp = "idk"
""" 