from tkinter import *
from tkinter import ttk
from tkinter import filedialog
# from matplotlib.backends.back_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# from matplotlib.figure import Figure

# import pyaudio, wave
import struct
import numpy as np
import matplotlib.pyplot as plt
import math
import cmath


def microphone():
    global RATE
    RATE = 44100
    FRAMES = 2**15
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


def wave_file(file):
    global RATE
    FRAMES = 2**17
    wf = wave.open(file, "rb")
    RATE = wf.getframerate()
    data = wf.readframes(FRAMES)
    wf.close()
    return data


def play(data, channels, RATE):
    p = pyaudio.PyAudio()
    play = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, output=True)
    play.write(data)
    play.stop_stream()
    play.close()
    p.terminate()


def getFundamentalFrequencies(data, plot=False):
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


def getNearestVowel(freq_funda, es_hombre=True):
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


def Select_file():
    
    filename = filedialog.askopenfilename(initialdir = "./", title = "Selecciona un achivo")

def Run():
    print(filename)
    result = getNearestVowel(getFundamentalFrequencies(wave_file(filename)))
    result_lbl.configure(text="La vocal es: "+result)


if __name__ == '__main__':
    
    filename = ""
    
    window = Tk()
    window.title("Deteccion de vocales")
    
    input_frame = Frame(window)
    input_frame.pack()
    
    input_lbl = Label(input_frame, text="Ingresa un audio:")
    search_btn = Button(input_frame, text="Buscar", command=Select_file)
    record_btn = Button(input_frame, text="Grabar")
    play_btn = Button(input_frame, text="Reproducir")
    gender_lbl = Label(input_frame, text="Selecciona una opcion: ")
    gender_combo = ttk.Combobox(input_frame, 
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
    exec_btn.grid(row=4)
    
    result_frame = Frame(window)
    result_frame.pack()
    
    result_lbl = Label(result_frame, text="Resultado")
    result_lbl.pack()

    
    window.mainloop()
    
    
    
