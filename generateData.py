import os 
from PIL import Image
import wave
import time
import matplotlib
import scipy.misc
from matplotlib import pylab
from pylab import *


def convert(image) :
    sound_info, frame_rate = get_wav_info(image)
    un,d,t,im = pylab.specgram(sound_info, Fs=frame_rate)
    im = Image.fromarray(un)
    if im.mode != 'RGB':
        im = im.convert('1')
        
    return im


def get_wav_info(wav_file):
    wav = wave.open(wav_file, 'r')
    frames = wav.readframes(-1)
    sound_info = pylab.fromstring(frames, 'Int16')
    frame_rate = wav.getframerate()
    wav.close()
    
    return sound_info, frame_rate


def main() :
    wav = "./wav/"
    paths = os.listdir(wav)
    labels = ["yes", "no", "up", "down", "left", "right", "on", "off", "stop", "go"]
    unknown = []
    files = {'unknown':[]}
    for p in paths :
        if p in labels :
            files[p] = [wav+p+'/'+pp for pp in os.listdir(wav+p)]
        else :
            unknown.append(p)
            files['unknown'] += [wav+p+'/'+pp for pp in os.listdir(wav+p)]
    
    counter = -1
    beg = time.time()
    log = []
    print("Converting :")
    for label in files :
        counter += 1
        print('Converting ', label,'...', round((time.time()-beg)*1000)/1000, 'sec.')
        if label=='unknown' :
            print('unknown')
            # count = 0
            # for f in files[label] :
            #     count += 1
            #     if count%5000==0 :
            #         print('unknown :', count,'/',len(files[label]), '(',f,')')
            #     try :
            #         image = convert(f)
            #         splited = f.split('/') 
            #         image.save("./spectro_nb/label"+str(counter)+'_'+(splited[-2]+'_'+splited[-1]).split('.')[0]+".png")
            #     except :
            #         log.append(f)
            #         print("Couldn't convert", f)
        else :
            for f in files[label] :
                try :
                    image = convert(f)
                    splited = f.split('/') 
                    image.save("./spectro_nb/label"+str(counter)+'_'+(splited[-2]+'_'+splited[-1]).split('.')[0]+".png")
                except :
                    log.append(f)
                    print("Couldn't convert", f)
            
            
main()