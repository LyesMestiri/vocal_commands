import os
import wave
import pylab
from PIL import Image
import scipy.misc


def graph_spectrogram(wav_file, label):
    sound_info, frame_rate = get_wav_info(wav_file)
    un,d,t,im = pylab.specgram(sound_info, Fs=frame_rate)
    im = Image.fromarray(un)
    # print(len(d))
    # print(len(t))
    # print(len(un))
    if im.mode != 'RGB':
        im = im.convert('1')
    im.save('tmp/output.png')
    #im.save("spectro_F/" + str(label) + "_" + wav_file.split('/')[-1].split('\\')[-1].replace("wav", "png"))
def get_wav_info(wav_file):
    wav = wave.open(wav_file, 'r')
    frames = wav.readframes(-1)
    sound_info = pylab.fromstring(frames, 'Int16')
    frame_rate = wav.getframerate()
    wav.close()
    return sound_info, frame_rate
# if __name__ == '__main__':
#     wav_file = 'go.wav'
#     graph_spectrogram(wav_file)