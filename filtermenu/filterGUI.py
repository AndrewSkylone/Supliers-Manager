import tkinter as tk
import copy

FREE_MARK = ' '
EMPLOYER_INDEX = 3

class FilterGui(tk.Menu):
    def __init__(self, master=None, cnf={}, **kw):
        tk.Menu.__init__(self, master, cnf=cnf, **kw)

        self.__listeners = []
        self.__backup_orders = ()
        self.__filter_orders = ()
        self.vars = {'All' : tk.StringVar(), 'Free' : tk.StringVar()}

        self.create_widgets()
        self.display_all()

    def create_widgets(self):
        for label in self.vars:
            self.add_checkbutton(label=label, variable=self.vars[label], onvalue=label, offvalue='',
                                command=lambda label=label: self.on_checkbox_click(label=label))
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
            pass
    
    def subscribe(self, listener):
        self.__listeners.append(listener)
    
    def filter_orders(self, orders):
        return orders

    def on_filter_orders_changed(self):
        for listener in self.__listeners:
            if hasattr(listener, "on_filter_orders_changed"):
                listener.on_filter_orders_changed(orders=self.get_filter_orders())
    
    def on_checkbox_click(self, label):
        vars_ = self.vars

        if vars_[label].get():
            if label == 'All':
                self.display_all()
            elif label == 'Free':
                self.display_free()
            else:
                

        elif not vars_[label].get():
            if label == 'All':
                self.remove_all()
            elif label == 'Free':
                self.remove_free()
        
    def display_all(self):
        for label in self.vars:
            self.vars[label].set(label)
        self.set_filter_orders(orders=self.get_backup_orders())
    
    def remove_all(self):
        for label in self.vars:
            self.vars[label].set('')
        self.set_filter_orders(orders=[])    
    
    def remove_free(self):
        not_free = [order for order in self.get_filter_orders() if order[EMPLOYER_INDEX] != FREE_MARK]
        self.set_filter_orders(orders=not_free)

    def display_free(self):
        free = [order for order in self.get_filter_orders() if order[EMPLOYER_INDEX] == FREE_MARK]
        self.set_filter_orders(orders=free)
    