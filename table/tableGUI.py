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

        self.create_widgets()
    
    def create_widgets(self):
        self.table = TreeView(master=self, height=self.table_height, show="headings")
        self.table.grid(row=0, column=0)

class TreeView(ttk.Treeview):
    def __init__(self, master, height, **kw):
        ttk.Treeview.__init__(self, master, **kw)

        self.height = height

        self["columns"] = (0, 1, 2, 3)
        self.column(0, width=150)
        self.column(1, width=200)
        self.column(2, width=150)
        self.column(3, width=200)

        self.heading(0, text="№")
        self.heading(1, text="Creation date")
        self.heading(2, text="MYXL number")
        self.heading(3, text="User")

        for i in range(len(self.height)):
            self.insert("", "end", iid=i, tags="all")
        self.tag_configure("all", font=("Arial", 11))
        # self.tag_bind("all", "<Return>", self.open_selected)
        # self.tag_bind("all", "<Button-1>", self.toggle_selected)
        # self.tag_bind("all", "<Control-c>", self.copy_value)
    
    # def on_orders_changed(self, orders):
    #     self.set_table_orders(orders=orders)

    # def get_table_orders(self) -> list:
    #     return list(copy.deepcopy(self.__table_orders))
    
    # def set_table_orders(self, orders):
    #     self.__table_orders = tuple(copy.deepcopy(orders))
    #     self.on_table_orders_changed()

    # def on_table_orders_changed(self):
    #     self.show_page(page=int(self.page_entry.get()))

    # def show_page(self, page):
    #     pages = math.ceil(len(stats) / self.table_height)

    # def clear_table(self):
    #     for iid in range(self.table["height"]):
    #         self.table.item(iid, value=[" "] * 4)
