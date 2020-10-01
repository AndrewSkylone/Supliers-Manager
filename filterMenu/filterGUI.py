import tkinter as tk
import copy

class FilterGui(tk.Menu):
    def __init__(self, master=None, cnf={}, **kw):
        tk.Menu.__init__(self, master, cnf=cnf, **kw)

        self.__listeners = []
        self.__backup_orders = ()
        self.__filter_orders = ()
        self.vars = {'All' : tk.StringVar(), 'Free' : tk.StringVar()}

        self.create_widgets()

    def create_widgets(self):
        for label in self.vars:
            self.add_checkbutton(label=label, variable=self.vars[label], onvalue=label, offvalue=False,
                                command=lambda label=label: self.on_checkbutton_pressed(label=label))
        self.add_separator()

    def on_orders_changed(self, orders):
        self.__backup_orders = copy.deepcopy(orders)
        self.set_filter_orders(orders=self.filter_orders(orders=orders))
    
    def set_filter_orders(self, orders):
        self.__filter_orders = copy.deepcopy(orders)
        self.on_filter_orders_changed()
    
    def get_filter_orders(self) -> list:
        return copy.deepcopy(self.__filter_orders)

    def get_backup_orders(self) -> list:
        return (copy.deepcopy(self.__backup_orders))
    
    def on_employers_changed(self, employers):
        for employer in employers:
            self.vars.update({employer : tk.StringVar()})
        
        for label in self.vars:
            raise NotImplementedError
    
    def subscribe(self, listener):
        self.__listeners.append(listener)
    
    def filter_orders(self, orders):
        raise NotImplementedError

    def on_filter_orders_changed(self):
        for listener in self.__listeners:
            if hasattr(listener, "on_filter_orders_changed"):
                listener.on_filter_orders_changed(orders=self.get_filter_orders())
    
    def on_checkbutton_pressed(self, label):
        orders = self.get_filter_orders()

        print(self.vars[label].get())
    