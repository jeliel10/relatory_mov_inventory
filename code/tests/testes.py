import webbrowser  # Importação para chamar o navegador.
from calendar import isleap
from datetime import datetime, date
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.ttk import Combobox
import firebirdsql
from reportlab.pdfgen import canvas

tela1 = Tk()

tela2 = Tk()


class Home():

    def home2(self):
        self.tela2 = tela2

        self.tela2.geometry("350x350")
        self.tela2.configure(background= "Red")
        self.tela2.resizable(True, True)

        self.tela2.mainloop()
        self.tela1.destroy()

    def __init__(self):
        self.tela1 = tela1

        self.tela1.mainloop()
        self.bt_config = Button(self.tela1, text="Config", background="black", bd=5,
                                command=self.home2)
        self.bt_config.place(rely=0.01, relx=0.2, relwidth=0.25)
Home()