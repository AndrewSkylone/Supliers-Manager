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
        self.table = TreeView(master=self, app=self, height=self.table_height, show="headings")
        self.table.grid(row=0, column=0)

        self.navigator = Navigator(master=self, app=self)
        self.subscribe(self.navigator)
        self.navigator.grid(row=1, column=0, padx=5, pady=5, sticky='w')

    def get_table_orders(self) -> list:
        return list(copy.deepcopy(self.__table_orders))
    
    def set_table_orders(self, orders):
        self.__table_orders = tuple(copy.deepcopy(orders))
        self.on_table_orders_changed()

    def on_orders_changed(self, orders):
        table_orders = self.get_table_orders()
        self.set_table_orders(orders=orders)

        if len(table_orders) == len(orders):
            self.table.show_page(page=int(self.navigator.page.get()))
        else:
            self.navigator.page.set(1)        

    def subscribe(self, listener):
        self.__listeners.append(listener)

    def on_table_orders_changed(self):
        for listener in self.__listeners:
            listener.on_table_orders_changed(orders=self.get_table_orders())

class TreeView(ttk.Treeview):
    def __init__(self, master, app, **kw):
        ttk.Treeview.__init__(self, master, **kw)

        self.app = app

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

    def show_page(self, page):
        orders = self.app.get_table_orders()
        
        self.clear()
        index = (page - 1) * self["height"]
        for i, row in enumerate(orders[index : index + self["height"]]):
            self.item(i, values=row)

        self.selection_remove(self.get_children())

    def clear(self):
        for iid in range(self["height"]):
            self.item(iid, value=[" "] * 4)
    
class Navigator(tk.Frame):
    def __init__(self, master, app, cnf={}, **kw):
        tk.Frame.__init__(self, master, cnf, **kw)

        self.app = app
        self.__listeners = []

        self.page = tk.StringVar(value=1)
        self.page.trace('w', self.on_page_changed)
        self.pages = tk.StringVar(value="Page: 1 / 1")
        self.orders_num = tk.StringVar(value="Total items: 0")

        self.create_widgets()
    
    def create_widgets(self):
        buttons = ["First", "Previous", "Next", "Last"]

        for column, goto in zip((0, 1, 3, 4), buttons):
            button = tk.Button(self, text=goto, font=("Calibri", 12), width=7)
            button.config(command=lambda goto=goto: self.goto_page(goto_page=goto))
            button.grid(row=0, column=column, sticky="w"+"e")

        page_entry = tk.Entry(self, width=5, font=("Calibri", 16), justify="center")
        page_entry.bind("<Return>", lambda e: self.goto_page(goto_page=page_entry.get()))
        page_entry.grid(row=0, column=2, sticky="w"+"e")

        pages_entry = tk.Entry(self, state="readonly", textvariable=self.pages, bd=0, justify="left")
        pages_entry.grid(row=1, column=0, columnspan=2, pady=4, sticky="w")

        total_entry = tk.Entry(self, state="readonly", textvariable=self.orders_num, bd=0, justify="left")
        total_entry.grid(row=2, column=0, columnspan=2, sticky="w")

    def goto_page(self, goto_page : str):
        pages = self.get_pages_num()
        page = int(self.page.get())

        if goto_page == "Last":
            page = pages
        if goto_page == "First":
            page = 1
        if goto_page == "Previous":
            page -= 1
        if goto_page == "Next":
            page += 1
        if goto_page.isnumeric():
            page = int(goto_page)
        
        if 1 < page and page < pages:
            self.page.set(page)
    
    def subscribe(self, listener):
        self.__listeners.append(listener)    
    
    def on_page_changed(self, *args):
        pages = self.get_pages_num()
        page = int(self.page.get())        

        self.pages.set(f"Page: {page} / {pages}")

        for listener in self.__listeners:
            listener.on_page_changed(page=self.page.get())
    
    def get_pages_num(self) -> int:
        orders_num = len(self.app.get_table_orders())
        table_rows = self.app.table_height  

        return math.ceil(orders_num / table_rows)
 
    def on_table_orders_changed(self, orders):
        self.orders_num.set(f"Total items: {len(orders)}")