from tkinter import *
from tkinter import ttk
from matplotlib.backends.back_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplolib.figure import Figure


if __name__ == '__main__':
    
    window = Tk()
    window.title("Deteccion de vocales")
    
    input_frame = Frame(window)
    input_frame.pack()
    
    input_lbl = Label(input_frame, text="Ingresa un audio:")
    search_btn = Button(input_frame, text="Buscar")
    record_btn = Button(input_frame, text="Grabar")
    play_btn = Button(input_frame, text="Reproducir")
    gender_lbl = Label(input_frame, text="Selecciona una opcion: ")
    gender_combo = ttk.Combobox(input_frame, 
                            values = [
                                "Masculino",
                                "Femenino"
                            ])
    
    input_lbl.grid(row=1,column=1)
    search_btn.grid(row=1,column=2)
    record_btn.grid(row=2,column=1)
    play_btn.grid(row=2,column=2)
    gender_lbl.grid(row=3,column=1)
    gender_combo.grid(row=3,column=2)
    
    plot_frame = Frame(window)
    plot_frame.pack()
    

    
    window.mainloop()
    
    
    
