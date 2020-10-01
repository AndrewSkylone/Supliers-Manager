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
        self.vars = {'All' : tk.StringVar(), FREE_MARK : tk.StringVar()}

        self.create_widgets()

    def create_widgets(self):
        self.add_checkbutton(label='All', variable=self.vars['All'], onvalue='All', offvalue='',
                                command=lambda: self.on_checkbox_click(label='All'))
        self.add_checkbutton(label='Free', variable=self.vars[FREE_MARK], onvalue=FREE_MARK, offvalue='',
                                command=lambda: self.on_checkbox_click(label=FREE_MARK))
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
            self.add_checkbutton(label=employer, variable=self.vars[employer], onvalue=employer, offvalue='',
                                command=lambda label=employer: self.on_checkbox_click(label=label))
        
        self.check_all()
    
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
        orders = self.get_filter_orders()

        if vars_[label].get():
            if label == 'All':
                self.check_all()
                orders = self.get_backup_orders()
            else:
                orders += self.get_mark_orders(orders=self.get_backup_orders(), mark=label)

        else:
            if label == 'All':
                self.uncheck_all()
                orders = []
            else:
                orders = self.remove_mark_orders(orders=orders, mark=label)
        
        self.set_filter_orders(orders=orders)
        
    def check_all(self):
        for label in self.vars:
            self.vars[label].set(label)
    
    def uncheck_all(self):
        for label in self.vars:
            self.vars[label].set('')
    
    def get_mark_orders(self, orders, mark) -> list:
        return [order for order in orders if order[EMPLOYER_INDEX] == mark]
    
    def remove_mark_orders(self, orders, mark) -> list:
        return [order for order in orders if order[EMPLOYER_INDEX] != mark]

    
    