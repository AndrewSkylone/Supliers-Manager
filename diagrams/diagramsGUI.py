import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import copy

class Diagrams_Frame(tk.Frame):
    def __init__(self, master, app, cnf={}, **kw):
        tk.Frame.__init__(self, cnf=cnf, **kw)

        self.app = app

        self.__orders_data = {}
        self.h_fig, self.h_ax = plt.subplots()
        self.p_fig, self.p_ax = plt.subplots()

        self.tk_h_fig = FigureCanvasTkAgg(self.h_fig, master)
        self.tk_p_fig = FigureCanvasTkAgg(self.p_fig, master)

        self.create_widgets()
    
    def create_widgets(self):
        self.h_ax.hist([1, 2, 3])
        self.p_ax.pie([1, 2, 3])

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
        return
        self.clear()
    
    def grid(self, cnf={}, **kw):
        tk.Frame.grid(self, cnf=cnf, **kw)
        self.tk_h_fig.get_tk_widget().grid(cnf=cnf, **kw)
        kw['column'] += 1
        self.tk_p_fig.get_tk_widget().grid(cnf=cnf, **kw)
    
    def clear(self):
        for i in plt.get_fignums():
            for ax in plt.figure(i).axes:
                ax.clear()

if __name__ == "__main__":
    
    def on_close():
        root.destroy()
        plt.close('all')

    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_close)

    diagrams = Diagrams_Frame(master=root, app=root)
    diagrams.grid()
    
    root.mainloop()