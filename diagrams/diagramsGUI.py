import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import numpy as np
import copy

class Diagrams_Frame(tk.Frame):
    def __init__(self, master, app, cnf={}, **kw):
        tk.Frame.__init__(self, master, cnf=cnf, **kw)

        self.app = app

        self.__orders_data = {}
        self.b_ax = None
        self.p_ax = None
        self.tk_bar_fig = None
        self.tk_pie_fig = None

        self.create_widgets()
    
    def create_widgets(self):
        hist_fig, self.b_ax = plt.subplots()
        self.tk_bar_fig = FigureCanvasTkAgg(hist_fig, self)
        self.tk_bar_fig.get_tk_widget().grid(row=0, column=0)

        pie_fig, self.p_ax = plt.subplots()
        self.tk_pie_fig = FigureCanvasTkAgg(pie_fig, self)
        self.tk_pie_fig.get_tk_widget().grid(row=0, column=1)
        # hist_fig.set_dpi(100)

    def draw_diagrams(self):
        orders_data = self.get_orders_data()
        employers_data = self.get_orders_data()
        free_data = employers_data.pop('Free')

        employers = list(employers_data.keys())
        orders_nums = [len(employers_data[employer]) for employer in employers]

        self.draw_bar(labels=employers, height=orders_nums)
        # self.draw_pie()
    
    def draw_bar(self, labels, height):
        max_num = max(height)
        colors = []
        for num in height:
            color = self.get_value_RGB_color(num, max_num)
            colors.append(color)
        
        x = list(range(len(labels)))
        self.b_ax.bar(x=x, height=height, color=colors)
        self.b_ax.grid(True, which='both', axis='y', alpha=0.2)

    def draw_pie(self):
        self.p_ax.pie()
    
    def get_value_RGB_color(self, value, maxvalue) -> tuple:
        R, G = 0, 1
        RGB = [1, 1, 0]
        middle = maxvalue / 2

        if value < middle:
            factor = value / middle
            RGB[G] = 0 + factor * 1
        elif value > middle:
            factor = (value - middle) / middle
            RGB[R] = 1 - factor * 1
        else:
            RGB = RGB

        return RGB

    def on_orders_changed(self, orders):
        orders_data = {}
        employers_data = self.app.get_employers_data()

        for employer in employers_data:
            orders_data.update(employers_data.items())
        orders_data.update({'Free' : self.app.get_free_orders()})
        
        self.set_orders_data(data=orders_data)

    def set_orders_data(self, data : dict):
        self.__orders_data = data
        self.on_orders_data_changed()
    
    def get_orders_data(self) -> dict:
        return copy.deepcopy(self.__orders_data)
    
    def on_orders_data_changed(self):
        self.clear()
        self.draw_diagrams()

        self.update()
        
    def clear(self):
        for i in plt.get_fignums():
            for ax in plt.figure(i).axes:
                ax.clear()

    def update(self):            
        self.tk_bar_fig.draw()
        self.tk_pie_fig.draw()
        tk.Frame.update(self)

if __name__ == "__main__":
    
    def on_close():
        root.destroy()
        plt.close('all')

    import random
    def recalculate_data():
        data = {'Andrew' : ['Andrew'] * random.randint(1, 100),
                'Erik' : ['Erik'] * random.randint(1, 100),
                'Sanya' : ['Sanya'] * random.randint(1, 100),
                'Borya' : ['Borya'] * random.randint(1, 100),
                'Jeka' : ['Jeka'] * random.randint(1, 100),
                'Anya' : ['Anya'] * random.randint(1, 100),
                'Den' : ['Den'] * random.randint(1, 100),
                'Tolik' : ['Tolik'] * random.randint(1, 100),
                'Dana' : ['Dana'] * random.randint(1, 100),
                'Free' : ['free'] * random.randint(1, 100)}
        diagrams.set_orders_data(data=data)

    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_close)

    diagrams = Diagrams_Frame(master=root, app=root)
    diagrams.grid()

    recalculate_data()
    tk.Button(root, text='calculate', command=recalculate_data).grid()  
    tk.Button(root, text='clear data', command=diagrams.clear).grid()  
    
    root.mainloop()