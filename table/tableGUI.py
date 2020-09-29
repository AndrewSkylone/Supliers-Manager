import tkinter as tk
import tkinter.ttk as ttk
import copy
import math


class TableGUI(tk.Frame):
    def __init__(self, master, height, cnf={}, **kw):
        tk.Frame.__init__(self, master, cnf, **kw)

        self.table_height = height
        self.__table_orders = ()
        self.table = None
        self.navigator = None
        self.__listeners = []

        self.create_widgets()
    
    def create_widgets(self):
        self.table = TreeView(master=self, application=self, height=self.table_height, show="headings")
        self.table.grid(row=0, column=0)

        # self.navigator = Navigator(master=self, )

    def get_table_orders(self) -> list:
        return list(copy.deepcopy(self.__table_orders))
    
    def set_table_orders(self, orders):
        self.__table_orders = tuple(copy.deepcopy(orders))
        self.on_table_orders_changed()

    def on_orders_changed(self, orders):
        self.set_table_orders(orders=orders)
    
    def subscribe(self, listener):
        self.__listeners.append(listener)

    def on_table_orders_changed(self):
        for listener in self.__listeners:
            listener.on_table_orders_changed(orders=self.get_table_orders())

class TreeView(ttk.Treeview):
    def __init__(self, master, application, **kw):
        ttk.Treeview.__init__(self, master, **kw)

        self.app = application
        self.page = 1

        self["columns"] = (0, 1, 2, 3)
        self.column(0, width=150)
        self.column(1, width=200)
        self.column(2, width=150)
        self.column(3, width=200)

        self.heading(0, text="№")
        self.heading(1, text="Creation date")
        self.heading(2, text="MYXL number")
        self.heading(3, text="User")

        for i in range(self['height']):
            self.insert("", "end", iid=i, tags="all")
        self.tag_configure("all", font=("Arial", 11))
        # self.tag_bind("all", "<Return>", self.open_selected)
        # self.tag_bind("all", "<Button-1>", self.toggle_selected)
        # self.tag_bind("all", "<Control-c>", self.copy_value)

    def show_page(self, orders, page):
        pages = math.ceil(len(orders) / self["height"])

    def clear(self):
        for iid in range(self["height"]):
            self.item(iid, value=[" "] * 4)
    
