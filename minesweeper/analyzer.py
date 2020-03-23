from PyQt5 import QtCore as qtc
import numpy as np
from threading import Thread
from queue import Queue, Empty
import random as rd


#Fait passer les sons dans le réseau et renvoies la fonction associée
def network(sound) :
    #output = reseau(sound) #sort un vecteur de probas de taille 11
    output = rd.choice(np.identity(11)[2:]) #ligne a supprimer une fois le réseau raccordé
    commands = [('on',), ('off',), ('start',), ('go',), ('stop',), ('yes',), ('no',), ('left',), ('right',), ('up',), ('down',)]
    return commands[np.argmax(output)]

class Analyzer(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.out_q = Queue()

    def run(self):
        #Emplacement du fichier ou les sons sont enregistrés/lus
        sample_path = qtc.QDir.home().filePath('Documents/Cours/ING3/Projet/vocalCommand/vocal_commands/minesweeper/enregistrements/enr.wav')#'./enregistrements/enr.wav'
        
        with open(sample_path, 'rb') as f:
            total_audio = b''
            read_buffer = b'NOT EMPTY'
            while read_buffer != b'':
                read_buffer = f.read(32044) # bytes
                
                ret = network(read_buffer)
                self._respond(ret)

                total_audio += read_buffer

    def _respond(self, ret):
        self.out_q.put(
            ret
        )

    def read_response(self):
        try:
            return self.out_q.get(False)
        except Empty:
            return None