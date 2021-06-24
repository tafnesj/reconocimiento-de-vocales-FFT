# RECONOCIMIENTO DE VOCALES con FFT
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import tkinter.font as tkFont
import numpy as np
import pyaudio
import wave
import struct
import numpy as np
import matplotlib.pyplot as plt
import math
import cmath

# Función: Revertir la posición de los bloques
def reverseBits(x,h):
    rev = '{:0{h}b}'.format(x, h=h)
    return(int(rev[::-1], 2))

# Función: Implementación de la FFT  
def fft(signal):
    signal = list(np.copy(signal).astype(complex))
    # Iteramos por todas las capas de abajo hacia arriba
    n = len(signal)
    # Altura en potencias de 2
    h = int(math.log2(n))
    for x in range(0,n):
        # Llamado a la función de revertir
        rev_pos = reverseBits(x,h)
        if(rev_pos<x):
            # Swap
            signal[rev_pos], signal[x] = signal[x],signal[rev_pos]
    # Vamos por todas las capas
    for i in range(h-1,-1,-1):
        # Tamaño del bloque
        sz = 1<<(h-i);
        # Número de bloques
        blocks = 1<<i;
        # Cálculo de las omegas [precalculado]
        w = [cmath.exp(-2j * cmath.pi * k / sz) for k in range(sz//2)]
        # Procesamiento de cada bloque
        for j in range(0,blocks):
            start = sz*j
            # Transformar bloque actual
            for k in range(0, sz//2):
                u = signal[start+k]
                v = signal[start+k+(sz//2)] * w[k]
                # Pares
                signal[start+k] = u+v
                # Impares
                signal[start+k+(sz//2)] = u-v
    return np.array(signal)

# Función: Lectura de archivo de audio [muestras en el tiempo]
def wave_file(file):
    global RATE
    # Leer 2^16 muestras
    FRAMES = 2**17
    wf = wave.open(file, "rb")
    RATE = wf.getframerate()
    data = wf.readframes(FRAMES)
    wf.close()
    return data

# Función:: Graficar las señales
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

# Función: Extraer las frecuencias fundamentales
def getFundamentalFrequencies(data, plot=True):
    # Muestras hexadecimal a entero de 16 bits
    data = list(struct.unpack(str(len(data)//2) + 'h', data))
    SZ = 1
    # Potencia de 2 más cercana
    while SZ < len(data):
        SZ<<=1
    # Rellenamos de ceros
    while len(data) < SZ:
        data.append(0)
    
    # Hallar la DFT del audio
    frequencies = np.abs(fft(data)) # Tomamos sólo la magnitud
    # Usar la mitad de las frecuencias [izquierda]
    frequencies = frequencies[:len(data)//2]
    if plot:
        eje_t = np.arange(0, len(data)) / RATE
        # Gráfica: Tiempo
        graficar([eje_t], [data], ["Audio"], "Tiempo (s)", "Amplitud", "Entrada de audio")
        eje_f = np.arange(0, len(data)//2) / (len(data)/RATE)
        # Gráfica: Frecuencia
        graficar([eje_f], [frequencies], ["Audio"], "Frecuencia (Hz)", "Amplitud", "Entrada de audio", (0,4000))
    
    # Ajustar las frecuencias de acuerdo cn el espacio de muestreo
    freqs = [(frequencies[i],i / (len(data)/RATE)) for i in range(len(data)//2)]
    # Ordenar de mayor a menor
    freqs.sort(reverse=True)
    
    # Tomamos los 3 máximos
    freq_funda = [freqs[0][1]]
    # Iteramos por el arreglo de las frecuencias
    for i in range(1,len(freqs)):
        is_valid = True
        for j in freq_funda:
            # Tomamos la frecuencia siguiente qye cumpla el parámetro
            if(abs(j-freqs[i][1])<100):
                is_valid = False
        if(is_valid):
            freq_funda.append(freqs[i][1])
            if(len(freq_funda)==3):
                break
    # Si no existen 3 diferentes, colocamos un 0
    while(len(freq_funda)<3):
        freq_funda.append(0)

    # Ordenamos ascendentemente
    freq_funda.sort()
    return freq_funda

# Función: Frecuencia promedio
def train():
    freq_av_h = {'a':[0,0,0],'e':[0,0,0],'i':[0,0,0],'o':[0,0,0],'u':[0,0,0]}
    num_hombres = 1
    for h in range(1,num_hombres+1):
        for v in ['a','e','i','o','u']:
            freq_funda = getFundamentalFrequencies(wave_file(F"hombre_0{h}/{v}.wav"),False)
            # Promedio
            for x in range(3):
                freq_av_h[v][x]+=freq_funda[x]/num_hombres
    return freq_av_h

# Frecuencias mujeres
freq_mujeres = {'a':[903,1129,2031],'e':[430,538,2772],'i':[240,480,2897],'o':[421,634,846],'u':[271,584,825]}
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

# Identificar el patrón con la vocal más cercana
def getNearestVowel(freq_funda, es_hombre=False):
    min_dif = 1e9
    vowel = 'a'
    # Frecuencias en hombres
    if(es_hombre==True):
        for i,j in freq_hombres.items():
            # Distancia Manhattan del patrón actual con las frecuencias
            freq_dif = abs(freq_funda[0]-j[0])+abs(freq_funda[1]-j[1])+abs(freq_funda[2]-j[2])
            if(min_dif>freq_dif):
                min_dif = freq_dif
                vowel = i
    # Frecuencias en mujeres
    else:
        for i,j in freq_mujeres.items():
            # Distancia Manhattan del patrón actual con las frecuencias
            freq_dif = abs(freq_funda[0]-j[0])+abs(freq_funda[1]-j[1])+abs(freq_funda[2]-j[2])
            if(min_dif>freq_dif):
                min_dif = freq_dif
                vowel = i
    return vowel


def restore():
    return option.get()    
    
# Interfaz: Elegir archivo preguardado
def Select_file():
    global filename
    filename = filedialog.askopenfilename(initialdir = "./", title = "Selecciona un achivo")
    input_lbl.config(text=filename)

# Interfaz: Iniciar programa
def Run():
    gender = False
    if restore() == "Masculino":
        gender = True  
    # Resultado de la vocal
    result = getNearestVowel(getFundamentalFrequencies(wave_file(filename)), gender)
    result_lbl.configure(text="La vocal es: "+result)

# Interfaz: Reproducir archivo cargado
def Play_record():
    channels = 2
    play(wave_file(filename), channels, RATE)
    
# Interfaz: Grabar audio desde el micrófono
def Record():
    gender = False
    if restore() == "Masculino":
        gender = True  
    microphone_funda = getFundamentalFrequencies(microphone(), True)
    result = getNearestVowel(microphone_funda,gender)
    # Resultado de la vocal
    result_lbl.configure(text="La vocal es: "+result)

if __name__ == '__main__':
    # creación de la ventana de tkinter 
    window = Tk()
    window.title("Deteccion de vocales")
    window.geometry('1500x300')
    
    # Creación del frame para los botones y elementos de entrada
    input_frame = Frame(window)
    input_frame.pack()
    
    
    fontStyle = tkFont.Font(family="Lucida Grande", size=22)
    # Botones de interfaz
    input_lbl = Label(input_frame, text="Ingresa un audio:", font=fontStyle)
    search_btn = Button(input_frame, text="Buscar", command=Select_file, font=fontStyle, bg='#428df5')
    record_btn = Button(input_frame, text="Grabar", command=Record, font=fontStyle, bg='#f54e42')
    play_btn = Button(input_frame, text="Reproducir", command=Play_record, font=fontStyle, bg='#25cf2e')
    gender_lbl = Label(input_frame, text="Selecciona una opcion: ", font=fontStyle)
    
    option = StringVar()
    gender_combo = ttk.Combobox(input_frame,textvariable=option, 
                            values = [
                                "Masculino",
                                "Femenino"
                            ])    
    
    exec_btn = Button(input_frame, text="Ejecutar", command=Run, font=fontStyle)
    
    # Posicionamiento de los widgets dentro de la interfaz mediante grid
    input_lbl.grid(row=1,column=1)
    search_btn.grid(row=1,column=2)
    record_btn.grid(row=2,column=1)
    play_btn.grid(row=2,column=2)
    gender_lbl.grid(row=3,column=1)
    gender_combo.grid(row=3,column=2)
    exec_btn.grid(row=4,column=1)
    
    # Seleccion predeterminada de combobox
    gender_combo.current(1)
    
    # Creacion de un frame para el resultado 
    result_frame = Frame(window)
    result_frame.pack()
    
    fontStyle2 = tkFont.Font(family="Lucida Grande", size=32)
    result_lbl = Label(result_frame, text="Resultado", font=fontStyle2)
    result_lbl.pack()

    
    window.mainloop()
    
    
    
