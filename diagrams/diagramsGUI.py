import matplotlib.pyplot as plot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

class Diagrams_Frame(tk.Frame):
    def __init__(self, master, app, cnf={}, **kw):
        tk.Frame.__init__(self, cnf=cnf, **kw)

        self.app = app
    
    def on_orders_changed(self, orders):
        fig, ax = plot.subplots()
        employers = ['Erik', 'Dana', 'Andrew', 'Ludmyla', 'Olena Rychko', 'Mykhailo Khabibulin', 'Sveta']
        orders = [len(employer) for employer in employers]
        ax.barh(employers, orders, color=['red', 'blue', 'orange', 'green'])

        top = tk.Toplevel(root)
        tkFigure = FigureCanvasTkAgg(fig, top)
        tkFigure.get_tk_widget().grid()