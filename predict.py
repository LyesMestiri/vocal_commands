from scipy.io.wavfile import write
import numpy as np
import cv2
import wave
import pylab
from PIL import Image


def graph_spectrogram(wav_file, label):
    sound_info, frame_rate = get_wav_info(wav_file)
    un,_,_,im = pylab.specgram(sound_info, Fs=frame_rate)
    im = Image.fromarray(un)
    if im.mode != 'RGB':
        im = im.convert('1')
    im.save('tmp/output.png')


def get_wav_info(wav_file):
    wav = wave.open(wav_file, 'r')
    frames = wav.readframes(-1)
    sound_info = pylab.fromstring(frames, 'Int16')
    frame_rate = wav.getframerate()
    wav.close()
    return sound_info, frame_rate


# Given au audio track, predicts the output
def prediction(myrecording, model, fs, filePath = 'tmp/output.wav'):
    write(filePath, fs, myrecording) # Save as WAV filePath
    graph_spectrogram(filePath, 1)

    image = cv2.imread('tmp/output.png', 0) #Read image
    image_array = np.array([np.asarray(image)])
    image_format = image_array.reshape((1, 129, 124, 1)) #reshape

    prediction = model.predict(image_format) #sort un vecteur de probas de taille 11
    classes = ["no", "on", "go", "up", "stop", "off", "left", "right", "down", "yes", "<UNK>"]
    return classes[np.argmax(prediction)]