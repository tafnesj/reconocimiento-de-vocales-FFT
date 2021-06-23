from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from functools import partial
# from matplotlib.backends.back_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# from matplotlib.figure import Figure
import numpy as np
import pyaudio
import wave
import struct
import numpy as np
import matplotlib.pyplot as plt
import math
import cmath

def reverseBits(x,h):
    rev = '{:0{h}b}'.format(x, h=h)
    return(int(rev[::-1], 2))
    
def fft(signal):
    signal = list(np.copy(signal).astype(complex))
    # Iteramos por todas las capas de abajo hacia arriba
    n = len(signal)
    h = int(math.log2(n))
    for x in range(0,n):
        rev_pos = reverseBits(x,h)
        if(rev_pos<x):
            signal[rev_pos], signal[x] = signal[x],signal[rev_pos]
    for i in range(h-1,-1,-1):
        sz = 1<<(h-i);
        blocks = 1<<i;
        w = [cmath.exp(-2j * cmath.pi * k / sz) for k in range(sz//2)]
        # Procesamiento de cada bloque
        for j in range(0,blocks):
            start = sz*j
            # Transformar bloque actual
            for k in range(0, sz//2):
                u = signal[start+k]
                v = signal[start+k+(sz//2)] * w[k]
                signal[start+k] = u+v
                signal[start+k+(sz//2)] = u-v
    return np.array(signal)


def wave_file(file):
    global RATE
    global data
    FRAMES = 2**17
    wf = wave.open(file, "rb")
    RATE = wf.getframerate()
    data = wf.readframes(FRAMES)
    wf.close()
    return data

def graficar(data_x, data_y, legends, label_x, label_y, title, xlim = None):
    for i in range(0, len(data_x)):
        plt.plot(data_x[i], data_y[i], label = legends[i], marker = "o")
    if xlim:
        plt.xlim(xlim)
    plt.grid(True)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.title(title)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), shadow=True, ncol=4)
    plt.show()
    plt.clf()

def getFundamentalFrequencies(data, plot=True):
    data = list(struct.unpack(str(len(data)//2) + 'h', data))
    SZ = 1
    while SZ < len(data):
        SZ<<=1
    while len(data) < SZ:
        data.append(0)
        
    frequencies = np.abs(fft(data))
    frequencies = frequencies[:len(data)//2]
    if plot:
        eje_t = np.arange(0, len(data)) / RATE
        graficar([eje_t], [data], ["Audio"], "Tiempo (s)", "Amplitud", "Entrada de audio")
        eje_f = np.arange(0, len(data)//2) / (len(data)/RATE)
        graficar([eje_f], [frequencies], ["Audio"], "Frecuencia (Hz)", "Amplitud", "Entrada de audio", (0,4000))
    
    freqs = [(frequencies[i],i / (len(data)/RATE)) for i in range(len(data)//2)]
    freqs.sort(reverse=True)

    freq_funda = [freqs[0][1]]
    for i in range(1,len(freqs)):
        is_valid = True
        for j in freq_funda:
            if(abs(j-freqs[i][1])<100):
                is_valid = False
        if(is_valid):
            freq_funda.append(freqs[i][1])
            if(len(freq_funda)==3):
                break
    while(len(freq_funda)<3):
        freq_funda.append(0)

    freq_funda.sort()
    return freq_funda


def train():
    freq_av_h = {'a':[0,0,0],'e':[0,0,0],'i':[0,0,0],'o':[0,0,0],'u':[0,0,0]}
    num_hombres = 1
    for h in range(1,num_hombres+1):
        for v in ['a','e','i','o','u']:
            freq_funda = getFundamentalFrequencies(wave_file(F"hombre_0{h}/{v}.wav"),False)

            for x in range(3):
                freq_av_h[v][x]+=freq_funda[x]/num_hombres

    return freq_av_h

# Frecuencias mujeres
freq_mujeres = {'a':[903,1129,2031],'e':[430,648,2772],'i':[240,480,2897],'o':[421,634,846],'u':[271,584,825]}
# Frecuencias hombres
freq_hombres = train()

def microphone():
    global RATE
    RATE = 44100
    FRAMES = 2**16
    duration = FRAMES/RATE
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=FRAMES)
    # Leer la entrada del micrófono 
    data = stream.read(FRAMES)
    # Cerrar el micrófono
    stream.stop_stream()
    stream.close()
    p.terminate()
    return data


def play(data, channels, RATE):
    p = pyaudio.PyAudio()
    play = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, output=True)
    play.write(data)
    play.stop_stream()
    play.close()
    p.terminate()


def getNearestVowel(freq_funda, es_hombre=False):
    min_dif = 1e9
    vowel = 'a'
    # Frecuencias en hombres
    if(es_hombre==True):
        for i,j in freq_hombres.items():
            freq_dif = abs(freq_funda[0]-j[0])+abs(freq_funda[1]-j[1])+abs(freq_funda[2]-j[2])
            if(min_dif>freq_dif):
                min_dif = freq_dif
                vowel = i
    # Frecuencias en mujeres
    else:
        for i,j in freq_mujeres.items():
            freq_dif = abs(freq_funda[0]-j[0])+abs(freq_funda[1]-j[1])+abs(freq_funda[2]-j[2])
            if(min_dif>freq_dif):
                min_dif = freq_dif
                vowel = i
    return vowel


def restore():
    return option.get()    
    

def Select_file():
    global filename
    filename = filedialog.askopenfilename(initialdir = "./", title = "Selecciona un achivo")
    input_lbl.config(text=filename)


def Run():
    gender = False
    if restore() == "Masculino":
        gender = True  
        
    result = getNearestVowel(getFundamentalFrequencies(wave_file(filename)), gender)
    result_lbl.configure(text="La vocal es: "+result)


def Play_record():
    channels = 2
    RATE = 44100
    play(data, channels, RATE)
    

def Record():
    gender = False
    if restore() == "Masculino":
        gender = True  
    microphone_funda = getFundamentalFrequencies(microphone(), True)   
    result = getNearestVowel(microphone_funda,gender)
    result_lbl.configure(text="La vocal es: "+result)

if __name__ == '__main__':

    window = Tk()
    window.title("Deteccion de vocales")
    
    input_frame = Frame(window)
    input_frame.pack()
    
    input_lbl = Label(input_frame, text="Ingresa un audio:")
    search_btn = Button(input_frame, text="Buscar", command=Select_file)
    record_btn = Button(input_frame, text="Grabar", command=Record)
    play_btn = Button(input_frame, text="Reproducir", command=Play_record)
    gender_lbl = Label(input_frame, text="Selecciona una opcion: ")
    
    option = StringVar()
    gender_combo = ttk.Combobox(input_frame,textvariable=option, 
                            values = [
                                "Masculino",
                                "Femenino"
                            ])    
    
    exec_btn = Button(input_frame, text="Ejecutar", command=Run)
    
    
    input_lbl.grid(row=1,column=1)
    search_btn.grid(row=1,column=2)
    record_btn.grid(row=2,column=1)
    play_btn.grid(row=2,column=2)
    gender_lbl.grid(row=3,column=1)
    gender_combo.grid(row=3,column=2)
    exec_btn.grid(row=4,column=1)
    
    gender_combo.current(1)
    
    result_frame = Frame(window)
    result_frame.pack()
    
    result_lbl = Label(result_frame, text="Resultado")
    result_lbl.pack()

    
    window.mainloop()
    
    
    
